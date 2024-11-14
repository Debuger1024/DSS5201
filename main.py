import os
from dash import Dash
from flask import Flask

server = Flask(__name__)
app = Dash(__name__, server=server)

port = int(os.getenv("PORT", 10000))

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=port, debug=False)
