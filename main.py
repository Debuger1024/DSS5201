from src.app import app
import os

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
