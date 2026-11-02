"""Entry point: python app.py, then open http://127.0.0.1:8050"""
from src.dashboard.app import create_app

app = create_app()
server = app.server

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
