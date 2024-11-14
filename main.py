import sys
sys.path.append("src")  # 添加 src 路径到 Python 的搜索路径

from app import create_app
import os)

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 8050))  # 默认端口设为8050
    app.run_server(host="0.0.0.0", port=port)
