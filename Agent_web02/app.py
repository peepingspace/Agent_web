from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import sys
import os

print("=" * 50)
print("开始启动 Flask 后端服务...")
print("=" * 50)

try:
    print("[1/3] 导入 Flask 模块...")
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    print("✓ Flask 导入成功")
except Exception as e:
    print(f"✗ Flask 导入失败: {e}")
    print("请运行: pip install flask flask-cors")
    sys.exit(1)

print("\n[2/3] 导入 Agent 模块...")
try:
    from final08 import build_graph
    print("✓ Agent 模块导入成功")
except Exception as e:
    print(f"✗ Agent 模块导入失败: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
    print("\n可能的原因:")
    print("  1. 缺少依赖包，请运行: pip install langgraph langchain langchain-community langchain-deepseek langchain-chroma chromadb docx2txt python-dotenv requests")
    print("  2. API Key 未配置，请检查 .env 文件")
    sys.exit(1)

print("\n[3/3] 初始化 Agent 图...")
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

app = Flask(__name__)

# 从环境变量读取允许的前端域名
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5500,http://localhost:8080').split(',')
CORS(app, origins=allowed_origins)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('question', '')
        
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
        
        print(f"✓ 意图: {result['intent']}")
        print(f"✓ 回答: {result['answer'][:50]}...")
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'intent': result['intent']
        })
        
    except Exception as e:
        print(f"✗ 处理请求时出错: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n🚀 启动服务器...")
    print(f"📡 地址: http://0.0.0.0:{port}")
    print("💬 API: http://0.0.0.0:{port}/api/chat")
    print("\n按 Ctrl+C 停止服务\n")
    app.run(host='0.0.0.0', port=port, debug=False)