from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
import requests

load_dotenv()

# ====================== 模型初始化 ======================
from langchain_deepseek import ChatDeepSeek

def init_deepseek_chat():
    return ChatDeepSeek(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        temperature=0.1
    )

def init_qwen_embedding():
    return DashScopeEmbeddings(
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
        model="text-embedding-v3"
    )

llm = init_deepseek_chat()
embed = init_qwen_embedding()

# ====================== 状态定义 ======================
class AllState(TypedDict):
    question: str
    history: List[Dict[str, str]]
    intent: str
    context: str
    answer: str
    check_result: bool
    tool_result: str
    iteration: int

# ====================== 提示词 ======================
INTENT_PROMPT = """
你是意图识别机器人，只能输出以下选项之一：
rag, code, doctor, bilibili, normal_chat
规则：
- 包含BV/bv → 输出bilibili
- 代码相关 → 输出code
- 运动/健康/康复 → 输出doctor
- 知识库/文档相关 → 输出rag
- 其他 → 输出normal_chat

用户问题：{question}
输出：
"""

CHECK_PROMPT = """
结合用户问题检查以下回答是否准确、完整、无幻觉。
问题：{question}
回答：{answer}
如果满意输出：True，否则输出：False
只能输出True或False
"""

# ====================== RAG 加载 Word ======================
def load_all_words(folder_path="docs"):
    docs = []
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    for f in os.listdir(folder_path):
        if f.endswith(".docx"):
            loader = Docx2txtLoader(os.path.join(folder_path, f))
            docs.extend(loader.load())
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(docs)

def retrieve_rag(question: str) -> str:
    splits = load_all_words()
    if not splits:
        return "未找到任何文档"
    db = Chroma.from_documents(splits, embed)
    retriever = db.as_retriever(search_kwargs={"k": 2})
    docs = retriever.invoke(question)
    return "\n".join([d.page_content for d in docs])

# ====================== 工具 ======================
def tool_rag(question: str) -> str:
    print(" 调用【RAG知识库工具】")
    return retrieve_rag(question)

def tool_code(question: str) -> str:
    print(" 调用【代码解析工具】")
    return f"[代码助手]\n{question}"

def tool_doctor(question: str) -> str:
    print(" 调用【运动康复私人医生工具】")
    return f"[运动康复私人医生]\n{question}"


def tool_bilibili(input_str: str) -> str:
    print(" 调用【B站视频信息工具】")
    # 1. 从用户输入中提取BV号（兼容纯BV号/带描述的输入）
    import re
    bv_match = re.search(r"BV[0-9A-Za-z]{10}", input_str.strip())
    if not bv_match:
        return "❌ 未检测到有效BV号，请输入正确的BV号格式（如BV117411r7R1）"
    bv = bv_match.group()

    try:
        # 2. 必须加请求头，绕过B站基础反爬
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/"
        }
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv}"
        resp = requests.get(url, headers=headers, timeout=10)

        # 3. 先检查响应状态码，再解析JSON
        if resp.status_code != 200:
            return f"❌ API请求失败，状态码：{resp.status_code}"

        # 4. 安全解析JSON，处理空响应
        json_data = resp.json()
        if json_data.get("code") != 0:
            return f"❌ B站API返回错误：{json_data.get('message', '未知错误')}"

        data = json_data["data"]
        return (
            f"📺 B站视频信息\n"
            f"标题：{data['title']}\n"
            f"UP主：{data['owner']['name']}\n"
            f"播放量：{data['stat']['view']}\n"
            f"点赞数：{data['stat']['like']}\n"
            f"视频链接：https://www.bilibili.com/video/{bv}"
        )
    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求失败：{str(e)}"
    except ValueError as e:
        return f"❌ JSON解析失败，API返回非JSON内容：{str(e)}"
    except Exception as e:
        return f"❌ 获取失败：{str(e)}"

# ====================== Graph 节点 ======================
def node_intent(state: AllState):
    response = llm.invoke(INTENT_PROMPT.format(question=state["question"]))
    intent = response.content.strip()
    valid_intents = {"rag", "code", "doctor", "bilibili", "normal_chat"}
    if intent not in valid_intents:
        intent = "normal_chat"

    print(f"\n意图识别结果为：{intent}")
    return {"intent": intent}

def node_rag(state: AllState):
    ctx = tool_rag(state["question"])
    return {"context": ctx}

def node_tool(state: AllState):
    intent = state["intent"]
    q = state["question"]
    if intent == "code":
        res = tool_code(q)
    elif intent == "doctor":
        res = tool_doctor(q)
    elif intent == "bilibili":
        res = tool_bilibili(q.strip())
    else:
        res = ""
    return {"tool_result": res}

def node_generate(state: AllState):
    q = state["question"]
    ctx = state["context"]
    tool_res = state["tool_result"]
    if state["intent"] == "bilibili":
        return {"answer": tool_res}
    prompt = f"使用下面信息回答问题，简洁准确。\n信息：{ctx}\n{tool_res}\n问题：{q}\n回答："
    response = llm.invoke(prompt)
    ans = response.content
    return {"answer": ans}

def node_self_check(state: AllState):
    response = llm.invoke(CHECK_PROMPT.format(
        question=state["question"],
        answer=state["answer"]
    ))
    check_out = response.content.strip()
    ok = check_out == "True"
    return {"check_result": ok, "iteration": state["iteration"] + 1}

# ====================== 路由 ======================
def router_intent(state: AllState):
    i = state["intent"]
    if i == "rag":
        return "rag"
    elif i in ["code", "doctor", "bilibili"]:
        return "tool"
    else:
        return "generate"

def router_check(state: AllState):
    if state["check_result"] or state["iteration"] >= 3:
        return END
    return "generate"

# ====================== 构建图 ======================
def build_graph():
    builder = StateGraph(AllState)

    builder.add_node("intent", node_intent)
    builder.add_node("rag", node_rag)
    builder.add_node("tool", node_tool)
    builder.add_node("generate", node_generate)
    builder.add_node("check", node_self_check)

    builder.set_entry_point("intent")

    builder.add_conditional_edges(
        "intent",
        router_intent,
        {
            "rag": "rag",
            "tool": "tool",
            "generate": "generate"
        }
    )

    builder.add_edge("rag", "generate")
    builder.add_edge("tool", "generate")
    builder.add_edge("generate", "check")

    builder.add_conditional_edges(
        "check",
        router_check,
        {
            "generate": "generate",
            END: END
        }
    )

    return builder.compile()

# ====================== 运行 ======================
if __name__ == "__main__":
    app = build_graph()
    print("🤖 多工具智能AI助手（输入 exit 退出）")
    print("📁 请将 Word 文件放入 ./docs 文件夹")
    while True:
        user_input = input("\n你：")
        if user_input.strip().lower() in ["exit", "quit"]:
            print("👋 再见")
            break

        res = app.invoke({
            "question": user_input,
            "history": [],
            "intent": "",
            "context": "",
            "tool_result": "",
            "answer": "",
            "check_result": False,
            "iteration": 0
        })

        print("助手：", res["answer"])




































