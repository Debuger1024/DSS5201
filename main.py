import sys
sys.path.append("src")  # 添加 src 路径到 Python 的搜索路径

from my_dash import create_app

app = create_app()
port = int(os.getenv("PORT", 10000))

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=port, debug=False)
