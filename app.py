from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
from snake_logic import SnakeGame
from database import init_db, add_user, verify_user, add_score, get_leaderboard
import bcrypt
from flask import jsonify, request

app = Flask(__name__)
app.secret_key = "supersecretkey"

socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize DB on startup
init_db()

# ---------------------------
# ROUTES
# ---------------------------

@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")
    return redirect("/game")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].encode("utf-8")

        user = verify_user(username)

        if user:
            stored_hash = user[2]
            if bcrypt.checkpw(password, stored_hash):
                session["username"] = username
                return redirect("/game")

        return render_template("login.html", error="Invalid username or password. OR Sign up to create an account below.")

    return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].encode("utf-8")

        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        if add_user(username, hashed):
            return redirect("/login")
        else:
            return render_template("register.html", error="Username already exists")

    return render_template("register.html")

@app.route("/leaderboard-data")
def leaderboard_data():
    board = get_leaderboard()
    return jsonify([{"username": row[0], "score": row[1]} for row in board])



@app.route("/game")
def game():
    if "username" not in session:
        return redirect("/login")
    return render_template("game.html", username=session["username"])


@app.route("/leaderboard")
def leaderboard():
    board = get_leaderboard()
    return render_template("leaderboard.html", board=board)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------------------
# SOCKET.IO EVENTS
# ---------------------------

games = {}

@socketio.on("start_game")
def start_game(data):
    username = data["username"]
    games[username] = SnakeGame()
    emit("state_update", games[username].get_state())


@socketio.on("change_direction")
def change_direction(data):
    username = data["username"]
    direction = data["direction"]
    if username in games:
        games[username].change_direction(direction)


from flask import jsonify, request  # make sure request is imported

@socketio.on("tick")
def tick(data):
    username = data["username"]
    if username not in games:
        return

    game = games[username]
    game.step()

    if game.game_over:
        # ✅ only save once
        if not game.score_saved:
            add_score(username, game.score)
            game.score_saved = True

        # send game_over just to this client
        emit("game_over", {"score": game.score}, to=request.sid)
        return

    # normal update
    emit("state_update", game.get_state(), to=request.sid)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)


