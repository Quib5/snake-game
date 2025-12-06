let socket;
let username;
let gameOverLock = false;


function startSnake(user) {
    username = user;
    paused = false;

    // Show game & hide button
    document.getElementById("startBtn").style.display = "none";
    document.getElementById("gameContainer").style.display = "block";

    // Create socket
    socket = io();

    socket.emit("start_game", {username: username});

    socket.on("state_update", (state) => {
        if (!paused) {
            document.getElementById("scoreDisplay").textContent = state.score;
            draw(state.snake, state.food, state.score);
        }
    });

    socket.on("game_over", (data) => {

    if (gameOverLock) return;  // Ignore duplicates
    gameOverLock = true;

    clearInterval(tickInterval);
    tickInterval = null;

    paused = true;

    alert("Game Over! Score: " + data.score);

    window.location.reload();
});



    // Movement + Pause
    document.addEventListener("keydown", (e) => {
        // Pause toggle
        if (e.key.toLowerCase() === "p") {
            paused = !paused;
            if (paused) drawPause();
            return;
        }

        // Movement
        if (!paused && ["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) {
            let d = e.key.replace("Arrow", "").toUpperCase();
            socket.emit("change_direction", {username: username, direction: d});
        }
    });

    // Tick loop (only when not paused)
    tickInterval = setInterval(() => {
        if (!paused) {
            socket.emit("tick", {username: username});
        }
    }, 120);
}

function draw(snake, food, score) {
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    // Clear entire canvas ONCE
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw snake (fast path)
    ctx.fillStyle = "#00cc33";
    for (let i = 0; i < snake.length; i++) {
        let x = snake[i][0] * 20;
        let y = snake[i][1] * 20;
        ctx.fillRect(x, y, 18, 18);
    }

    // Draw food
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
