const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const BLOCK_SIZE = 20;
const COLUMNS = canvas.width / BLOCK_SIZE;
const ROWS = canvas.height / BLOCK_SIZE;
const PAUSE_TEXT = 'Press Start to play';

const scoreEl = document.getElementById('score');
const speedEl = document.getElementById('speed');
const statusEl = document.getElementById('status');
const menuScreen = document.getElementById('menuScreen');
const menuPlayBtn = document.getElementById('menuPlayBtn');
const menuContinueBtn = document.getElementById('menuContinueBtn');
const menuQuitBtn = document.getElementById('menuQuitBtn');
const scoresPanel = document.getElementById('scoresPanel');
const menuCurrentScore = document.getElementById('menuCurrentScore');
const menuBestScore = document.getElementById('menuBestScore');

let snake = [];
let direction = { x: 0, y: 0 };
let nextDirection = { x: 0, y: 0 };
let food = { x: 0, y: 0 };
let score = 0;
let highScore = 0;
let intervalId = null;
let gameSpeed = 10;
let running = false;
let gameOver = false;
let hasPlayed = false;

function loadHighScore() {
    const saved = localStorage.getItem('snakeGameHighScore');
    return saved ? parseInt(saved, 10) : 0;
}

function saveHighScore() {
    localStorage.setItem('snakeGameHighScore', highScore);
}

function resetGame() {
    snake = [{ x: Math.floor(COLUMNS / 2), y: Math.floor(ROWS / 2) }];
    direction = { x: 0, y: 0 };
    nextDirection = { x: 0, y: 0 };
    food = spawnFood();
    score = 0;
    gameOver = false;
    running = false;
    updateUi();
    draw();
}

function spawnFood() {
    let position;
    do {
        position = {
            x: Math.floor(Math.random() * COLUMNS),
            y: Math.floor(Math.random() * ROWS)
        };
    } while (snake.some(segment => segment.x === position.x && segment.y === position.y));

    return position;
}

function updateUi() {
    scoreEl.textContent = score;
    speedEl.textContent = gameSpeed;
    if (gameOver) {
        statusEl.textContent = 'Game Over';
        statusEl.classList.add('danger');
    } else if (!running) {
        statusEl.textContent = PAUSE_TEXT;
        statusEl.classList.remove('danger');
    } else {
        statusEl.textContent = 'Playing';
        statusEl.classList.remove('danger');
    }
}

function showMenuScreen() {
    updateMenuScores();
    menuContinueBtn.classList.toggle('hidden', !hasPlayed);
    menuScreen.classList.remove('hidden');
}

function hideMenuScreen() {
    menuScreen.classList.add('hidden');
}

function updateMenuScores() {
    menuCurrentScore.textContent = score;
    menuBestScore.textContent = highScore;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // draw food
    ctx.fillStyle = '#ff4d4d';
    ctx.fillRect(food.x * BLOCK_SIZE, food.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);

    // draw snake
    ctx.fillStyle = '#4ade80';
    snake.forEach((segment, index) => {
        ctx.fillRect(segment.x * BLOCK_SIZE, segment.y * BLOCK_SIZE, BLOCK_SIZE - 2, BLOCK_SIZE - 2);
        if (index === snake.length - 1) {
            ctx.fillStyle = '#d8f5a2';
            ctx.fillRect(segment.x * BLOCK_SIZE + 2, segment.y * BLOCK_SIZE + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4);
            ctx.fillStyle = '#4ade80';
        }
    });
}

function update() {
    if (gameOver || (direction.x === 0 && direction.y === 0)) {
        return;
    }

    direction = nextDirection;
    const head = { x: snake[snake.length - 1].x + direction.x, y: snake[snake.length - 1].y + direction.y };

    if (head.x < 0) head.x = COLUMNS - 1;
    if (head.x >= COLUMNS) head.x = 0;
    if (head.y < 0) head.y = ROWS - 1;
    if (head.y >= ROWS) head.y = 0;

    if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
        endGame();
        return;
    }

    snake.push(head);

    if (head.x === food.x && head.y === food.y) {
        score += 1;
        food = spawnFood();
    } else {
        snake.shift();
    }

    draw();
    updateUi();
}

function startGame() {
    hasPlayed = true;
    if (gameOver) {
        resetGame();
    }
    hideMenuScreen();
    if (!running) {
        running = true;
        if (direction.x === 0 && direction.y === 0) {
            direction = { x: 1, y: 0 };
            nextDirection = { x: 1, y: 0 };
        }
        intervalId = setInterval(update, 1000 / gameSpeed);
        updateUi();
    }
}

function continueGame() {
    if (gameOver) {
        resetGame();
    }
    hideMenuScreen();
    if (!running) {
        startGame();
    }
}

function pauseGame() {
    if (!running) {
        return;
    }
    clearInterval(intervalId);
    running = false;
    statusEl.textContent = 'Paused';
    updateUi();
    showMenuScreen();
}

function endGame() {
    const newHighScore = Math.max(highScore, score);
    if (newHighScore > highScore) {
        highScore = newHighScore;
        saveHighScore();
    }
    gameOver = true;
    running = false;
    clearInterval(intervalId);
    statusEl.textContent = 'Game Over';
    updateUi();
    showMenuScreen();
}

function restartGame() {
    clearInterval(intervalId);
    resetGame();
    startGame();
}

function setDirection(newDirection) {
    const opposite = direction.x === -newDirection.x && direction.y === -newDirection.y;
    if (!opposite) {
        nextDirection = newDirection;
    }
}

window.addEventListener('keydown', event => {
    const key = event.key.toLowerCase();
    const keys = {
        arrowup: { x: 0, y: -1 },
        arrowdown: { x: 0, y: 1 },
        arrowleft: { x: -1, y: 0 },
        arrowright: { x: 1, y: 0 },
        w: { x: 0, y: -1 },
        s: { x: 0, y: 1 },
        a: { x: -1, y: 0 },
        d: { x: 1, y: 0 }
    };

    if (key === 'p') {
        pauseGame();
        return;
    }
    if (key === 'r') {
        restartGame();
        return;
    }

    const directionValue = keys[event.key] || keys[key];
    if (directionValue) {
        event.preventDefault();
        if (!running && !gameOver) {
            startGame();
        }
        setDirection(directionValue);
    }
});

menuPlayBtn.addEventListener('click', () => {
    resetGame();
    hideMenuScreen();
    startGame();
});
menuContinueBtn.addEventListener('click', continueGame);
menuQuitBtn.addEventListener('click', () => {
    window.location.href = '/';
});

highScore = loadHighScore();
resetGame();
showMenuScreen();
