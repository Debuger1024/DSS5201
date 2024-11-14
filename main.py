from src.app import app
import os

port = int(os.environ.get("PORT", 10000))

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=port, debug=True)

