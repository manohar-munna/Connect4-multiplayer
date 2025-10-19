document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const gameBoard = document.getElementById('game-board');
    const createGameBtn = document.getElementById('create-game');
    const joinGameBtn = document.getElementById('join-game');
    const roomInput = document.getElementById('room-input');
    const gameStatus = document.getElementById('game-status');
    let currentRoom = '';
    let playerColor = '';

    const createBoard = () => {
        for (let r = 0; r < 6; r++) {
            for (let c = 0; c < 7; c++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.row = r;
                cell.dataset.column = c;
                cell.addEventListener('click', () => handleCellClick(c));
                gameBoard.appendChild(cell);
            }
        }
    };

    const handleCellClick = (column) => {
        console.log('=== CELL CLICKED ===');
        console.log('Column:', column);
        console.log('currentRoom:', currentRoom);
        console.log('playerColor:', playerColor);
        console.log('socket.connected:', socket.connected);
        
        if (currentRoom) {
            console.log('Emitting make_move event...');
            socket.emit('make_move', { room: currentRoom, column: column });
        } else {
            console.log('ERROR: No current room set!');
        }
    };

    createGameBtn.addEventListener('click', () => {
        const room = roomInput.value;
        if (room) {
            console.log('Creating game in room:', room);
            socket.emit('create_game', { room: room });
        }
    });

    joinGameBtn.addEventListener('click', () => {
        const room = roomInput.value;
        if (room) {
            console.log('Joining game in room:', room);
            socket.emit('join_game', { room: room });
        }
    });

    socket.on('game_created', (data) => {
        console.log('Game created event received:', data);
        currentRoom = data.room;
        playerColor = data.player;
        gameStatus.textContent = `Game room "${currentRoom}" created. You are the ${playerColor} player. Waiting for opponent...`;
    });

    socket.on('game_joined', (data) => {
        console.log('Game joined event received (I am yellow!):', data);
        currentRoom = data.room;
        playerColor = data.player;
        gameStatus.textContent = `Joined room "${currentRoom}". You are the ${playerColor} player. Waiting for game to start...`;
    });

    socket.on('player_joined', (data) => {
        console.log('Player joined event received:', data);
        // This is for the red player seeing yellow join
        if (playerColor === 'red') {
            gameStatus.textContent = `Yellow player has joined! Game starting...`;
        }
    });

    socket.on('start_game', (data) => {
        console.log('Start game event received:', data);
        gameStatus.textContent = `Game started! It is ${data.turn}'s turn.`;
    });

    socket.on('move_made', (data) => {
        console.log('Move made event received:', data);
        const cell = document.querySelector(`.cell[data-row='${data.row}'][data-column='${data.column}']`);
        if (cell) {
            cell.classList.add(data.color);
            gameStatus.textContent = `It is ${data.turn}'s turn.`;
        } else {
            console.log('ERROR: Could not find cell at row', data.row, 'column', data.column);
        }
    });

    socket.on('game_over', (data) => {
        console.log('Game over event received:', data);
        gameStatus.textContent = `Game over! ${data.winner.charAt(0).toUpperCase() + data.winner.slice(1)} wins!`;
        currentRoom = '';
    });

    socket.on('error', (data) => {
        console.log('Error event received:', data);
        alert(data.message);
    });

    // Add connection debugging
    socket.on('connect', () => {
        console.log('Socket connected! Socket ID:', socket.id);
    });

    socket.on('disconnect', () => {
        console.log('Socket disconnected!');
    });

    createBoard();
});