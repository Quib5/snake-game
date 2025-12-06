let socket;
let username;

function startSnake(user) {
    username = user;
    socket = io();

    socket.emit("start_game", {username: username});

    socket.on("state_update", (state) => {
    document.getElementById("scoreDisplay").textContent = state.score;
    draw(state.snake, state.food, state.score);
    });


    socket.on("game_over", (data) => {
        alert("Game Over! Score: " + data.score);
        window.location.href = "/leaderboard";
    });

    document.addEventListener("keydown", (e) => {
        if (["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) {
            let d = e.key.replace("Arrow", "").toUpperCase();
            socket.emit("change_direction", {username: username, direction: d});
        }
    });

    setInterval(() => {
        socket.emit("tick", {username: username});
    }, 150);
}

function draw(snake, food, score) {
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, 400, 400);

    ctx.fillStyle = "lime";
    snake.forEach(([x, y]) => {
        ctx.fillRect(x * 20, y * 20, 18, 18);
    });

    ctx.fillStyle = "red";
    ctx.fillRect(food[0] * 20, food[1] * 20, 18, 18);
}

// LIVE LEADERBOARD POLLING
function updateLeaderboard() {
    fetch("/leaderboard-data")
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById("leaderboardList");
            list.innerHTML = "";
            data.forEach(item => {
                const li = document.createElement("li");
                li.textContent = `${item.username}: ${item.score}`;
                list.appendChild(li);
            });
        });
}

setInterval(updateLeaderboard, 1500); // update every 1.5s
