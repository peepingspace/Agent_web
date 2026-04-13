const agents = [
  { key: "study", name: "📖学业agent", guide: "你想了解哪些课程安排或学业政策？", intent: "学业查询" },
  { key: "activity", name: "🪁活动agent", guide: "你想了解什么方面的校园活动？", intent: "活动咨询" },
  { key: "party", name: "🀄党团agent", guide: "你想了解党团事务的哪些内容？", intent: "党团服务" },
  { key: "career", name: "🎓就业agent", guide: "你想了解实习、就业还是招聘信息？", intent: "就业咨询" },
  { key: "admin", name: "💼行政agent", guide: "你想办理哪项行政事务？", intent: "行政办理" }
];

const agentTabs = document.getElementById("agentTabs");
const chatInput = document.getElementById("chatInput");
const chatBoard = document.getElementById("chatBoard");
const routeLine = document.getElementById("routeLine");
let currentAgent = agents[0];

// 从环境变量或配置中获取后端地址
const BACKEND_URL = window.ENV?.BACKEND_URL || 'https://agent-web-l9y3.onrender.com';

function renderAgentTabs() {
  agentTabs.innerHTML = "";
  agents.forEach((agent) => {
    const btn = document.createElement("button");
    btn.textContent = agent.name;
    if (agent.key === currentAgent.key) {
      btn.classList.add("active");
    }
    btn.addEventListener("click", () => {
      currentAgent = agent;
      chatInput.placeholder = agent.guide;
      renderAgentTabs();
      const tip = document.createElement("div");
      tip.className = "msg bot";
      tip.textContent = `已切换到${agent.name}，${agent.guide}`;
      chatBoard.appendChild(tip);
      chatBoard.scrollTop = chatBoard.scrollHeight;
    });
    agentTabs.appendChild(btn);
  });
}

renderAgentTabs();

async function sendMessageToBackend(question) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: question
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) {
    return;
  }

  const userMsg = document.createElement("div");
  userMsg.className = "msg user";
  userMsg.textContent = text;
  chatBoard.appendChild(userMsg);

  chatInput.value = "";
  chatBoard.scrollTop = chatBoard.scrollHeight;

  const loadingMsg = document.createElement("div");
  loadingMsg.className = "msg bot";
  loadingMsg.textContent = "正在思考中...";
  chatBoard.appendChild(loadingMsg);
  chatBoard.scrollTop = chatBoard.scrollHeight;

  try {
    const result = await sendMessageToBackend(text);
    
    chatBoard.removeChild(loadingMsg);
    
    const botMsg = document.createElement("div");
    botMsg.className = "msg bot";
    botMsg.innerHTML = `<strong>[${result.intent || '智能助手'}]</strong><br/>${result.answer}`;
    chatBoard.appendChild(botMsg);
    chatBoard.scrollTop = chatBoard.scrollHeight;
    
  } catch (error) {
    chatBoard.removeChild(loadingMsg);
    const errorMsg = document.createElement("div");
    errorMsg.className = "msg bot";
    errorMsg.textContent = "抱歉，服务暂时不可用，请稍后再试。";
    chatBoard.appendChild(errorMsg);
    chatBoard.scrollTop = chatBoard.scrollHeight;
  }
}

document.getElementById("sendBtn").addEventListener("click", sendMessage);
chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});
