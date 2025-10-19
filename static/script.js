document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const gameBoard = document.getElementById('game-board');
    const gameControls = document.getElementById('game-controls');
    const gameOverControls = document.getElementById('game-over-controls');
    const createGameBtn = document.getElementById('create-game');
    const joinGameBtn = document.getElementById('join-game');
    const roomInput = document.getElementById('room-input');
    const gameStatus = document.getElementById('game-status');
    const rematchBtn = document.getElementById('rematch-btn');
    const newGameBtn = document.getElementById('new-game-btn');

    let currentRoom = '';
    let playerColor = '';
    let isMyTurn = false;

    const createBoard = () => {
        gameBoard.innerHTML = ''; // Clear previous board
        for (let r = 0; r < 6; r++) {
            for (let c = 0; c < 7; c++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.addEventListener('click', () => handleCellClick(c));
                gameBoard.appendChild(cell);
            }
        }
    };

    const handleCellClick = (column) => {
        if (isMyTurn) {
            socket.emit('make_move', { room: currentRoom, column: column });
        }
    };

    const updateBoardTurnIndicator = () => {
        gameBoard.classList.toggle('my-turn', isMyTurn);
    };

    // --- Button Event Listeners ---
    createGameBtn.addEventListener('click', () => {
        currentRoom = roomInput.value;
        if (currentRoom) socket.emit('create_game', { room: currentRoom });
    });

    joinGameBtn.addEventListener('click', () => {
        currentRoom = roomInput.value;
        if (currentRoom) socket.emit('join_game', { room: currentRoom });
    });

    rematchBtn.addEventListener('click', () => {
        socket.emit('rematch_request', { room: currentRoom });
        gameStatus.textContent = 'Waiting for opponent to accept rematch...';
        rematchBtn.disabled = true;
    });

    newGameBtn.addEventListener('click', () => {
        window.location.reload();
    });

    // --- Socket.IO Event Handlers ---
    socket.on('game_created', (data) => {
        gameControls.style.display = 'none';
        gameStatus.textContent = `Room "${data.room}" created. Waiting for opponent...`;
    });
    
    socket.on('start_game', (data) => {
        gameControls.style.display = 'none';
        gameOverControls.style.display = 'none';
        gameBoard.style.display = 'grid'; // Make sure board is visible
        createBoard(); // Reset board for rematches

        playerColor = data.color;
        isMyTurn = (playerColor === data.turn);
        
        const turnColor = data.turn.charAt(0).toUpperCase() + data.turn.slice(1);
        gameStatus.textContent = `You are ${playerColor}. It is ${turnColor}'s turn.`;
        updateBoardTurnIndicator();
    });

    socket.on('move_made', (data) => {
        const cellsInColumn = Array.from(document.querySelectorAll('.cell')).filter(c => c.dataset.column === String(data.column));
        cellsInColumn[data.row].classList.add(data.color);
        
        isMyTurn = (playerColor === data.turn);
        
        const turnColor = data.turn.charAt(0).toUpperCase() + data.turn.slice(1);
        gameStatus.textContent = `It is ${turnColor}'s turn.`;
        updateBoardTurnIndicator();
    });

    socket.on('game_over', (data) => {
        isMyTurn = false;
        const winnerColor = data.winner.charAt(0).toUpperCase() + data.winner.slice(1);
        gameStatus.textContent = `Game over! ${winnerColor} wins!`;
        
        gameBoard.style.display = 'none';
        gameOverControls.style.display = 'flex';
        rematchBtn.disabled = false;
    });

    socket.on('opponent_wants_rematch', () => {
        gameStatus.textContent = 'Your opponent wants a rematch!';
    });

    socket.on('player_disconnected', (data) => {
        isMyTurn = false;
        gameStatus.textContent = data.message;
        gameBoard.style.display = 'none';
        gameOverControls.style.display = 'none';
    });

    socket.on('error', (data) => {
        alert(data.message);
    });

    createBoard();
});
