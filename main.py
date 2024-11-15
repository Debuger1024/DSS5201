import sys
sys.path.append("src")  # 添加 src 路径到 Python 的搜索路径

from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run_server(debug=True)

