import queue
import threading
import time

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "justasecretkeythatishouldputhere"

socketio = SocketIO(app)
CORS(app)

q = queue.LifoQueue()


def background():
    rept = 0
    while rept <= 1000:
        q.put({"repeticao": rept})
        socketio.emit("back", dict(data=f"teste{rept}"), broadcast=True)
        rept += 1
        time.sleep(5)


thread = threading.Thread(target=background, daemon=True)
thread.start()


@app.route("/")
def index():
    print(q.get())
    return render_template("index.html")


@app.route("/api")
def api():
    query = dict(request.args)
    socketio.emit("log", dict(data=str(query)), broadcast=True)
    return jsonify(dict(success=True, message="Received"))


@socketio.on("connect")
def on_connect():
    payload = dict(data="Connected")
    emit("log", payload, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, debug=True)
