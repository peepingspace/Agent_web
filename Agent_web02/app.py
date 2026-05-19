print("🔥 程序开始执行！")
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import sys
import os

print("=" * 50)
print("开始启动 Flask 后端服务...")
print("=" * 50)

# ====================== 导入 Agent ======================
print("\n[1/2] 导入 Agent 模块...")
try:
    from Agent import build_graph
    print("✓ Agent 模块导入成功")
except Exception as e:
    print(f"✗ Agent 模块导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# ====================== 初始化 Agent ======================
print("\n[2/2] 初始化 Agent 图...")
try:
    agent_graph = build_graph()
    print("✓ Agent 图初始化成功")
except Exception as e:
    print(f"✗ Agent 图初始化失败: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("✓ 所有模块加载完成！")
print("=" * 50)

# ====================== Flask 初始化 ======================
app = Flask(__name__)

# 🔥 修复跨域：允许所有来源访问（本地开发必开）
CORS(app, resources={r"/*": {"origins": "*"}})

# ====================== 聊天接口 ======================
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        print(f"\n📨 收到问题: {question}")
        
        result = agent_graph.invoke({
            "question": question,
            "history": [],
            "intent": "",
            "context": "",
            "tool_result": "",
            "answer": "",
            "check_result": False,
            "iteration": 0
        })
        
        answer = result.get("answer", "未生成回答")
        intent = result.get("intent", "unknown")
        
        print(f"✓ 意图: {intent}")
        print(f"✓ 回答: {answer[:50]}...")
        
        return jsonify({
            'success': True,
            'answer': answer,
            'intent': intent
        })
        
    except Exception as e:
        print(f"✗ 处理请求出错: {e}")
        traceback.print_exc()
        return jsonify({'error': f'服务器错误：{str(e)}'}), 500

# ====================== 健康检查 ======================
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Backend is running',
        'agent_loaded': True
    })

# ====================== 启动 ======================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    
    # app.run(host='0.0.0.0', port=port, debug=False)  # 关闭 debug
    # print("\n🚀 服务器启动成功！")
    # print(f"📡 访问地址: http://127.0.0.1:{port}")
    # print(f"💬 聊天接口: http://127.0.0.1:{port}/api/chat")
    # print(f"✅ 健康检查: http://127.0.0.1:{port}/health")
    # print("\n按 Ctrl+C 停止服务\n")
    # app.run(host='0.0.0.0', port=port, debug=True)

    # ====================== 【修复版：正确启动，只运行一次 app.run】======================
    print("\n🚀 服务器启动成功！")
    print(f"📡 访问地址: http://127.0.0.1:{port}")
    print(f"💬 聊天接口: http://127.0.0.1:{port}/api/chat")
    print(f"✅ 健康检查: http://127.0.0.1:{port}/health")
    print("\n按 Ctrl+C 停止服务\n")

    # 🔥 关键修复：只启动一次服务器，不会崩溃
    app.run(host='0.0.0.0', port=port, debug=True)
