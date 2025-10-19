from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key'
socketio = SocketIO(app)

# A dictionary to store the state of active games
games = {}

@app.route('/')
def index():
    """Serves the main game page."""
    return render_template('index.html')

@socketio.on('create_game')
def create_game(data):
    """Creates a new game room."""
    room = data['room']
    if room not in games:
        games[room] = {
            'players': [request.sid],
            'board': [['' for _ in range(7)] for _ in range(6)],
            'turn': request.sid,
            'player_colors': {request.sid: 'red'}
        }
        join_room(room)
        emit('game_created', {'room': room, 'player': 'red'})
        print(f"Game created in room {room}. Red player: {request.sid}")
    else:
        emit('error', {'message': 'Game room already exists.'})

@socketio.on('join_game')
def join_game(data):
    """Allows a second player to join a game room."""
    room = data['room']
    if room in games and len(games[room]['players']) == 1:
        games[room]['players'].append(request.sid)
        games[room]['player_colors'][request.sid] = 'yellow'
        join_room(room)
        
        print(f"Yellow player joined room {room}. Yellow player: {request.sid}")
        print(f"Current turn is: {games[room]['turn']}")
        
        # CRITICAL FIX: Send confirmation directly to yellow first
        emit('game_joined', {'room': room, 'player': 'yellow'})
        
        # Then notify the room that yellow joined
        emit('player_joined', {'room': room, 'player': 'yellow'}, to=room)
        
        # Send game start to both players
        emit('start_game', {'turn': 'red'}, to=room)
    else:
        emit('error', {'message': 'Game room is full or does not exist.'})

@socketio.on('make_move')
def make_move(data):
    """Handles a player making a move."""
    room = data['room']
    column = data['column']
    player_sid = request.sid

    print(f"\n=== MOVE ATTEMPT ===")
    print(f"Room: {room}")
    print(f"Player SID making move: {player_sid}")
    print(f"Column: {column}")
    
    if room not in games:
        print(f"ERROR: Room {room} does not exist")
        emit('error', {'message': 'Game room does not exist.'})
        return
    
    print(f"Current turn SID: {games[room]['turn']}")
    print(f"Player color: {games[room]['player_colors'].get(player_sid, 'UNKNOWN')}")
    print(f"Is player's turn? {games[room]['turn'] == player_sid}")
    
    if games[room]['turn'] == player_sid:
        board = games[room]['board']
        color = games[room]['player_colors'][player_sid]

        # Find the first available row in the selected column
        for r in range(5, -1, -1):
            if board[r][column] == '':
                board[r][column] = color
                
                # Switch turns
                next_player_sid = next(p for p in games[room]['players'] if p != player_sid)
                games[room]['turn'] = next_player_sid
                next_player_color = games[room]['player_colors'][next_player_sid]

                print(f"Move successful! Next turn: {next_player_color} (SID: {next_player_sid})")

                # Emit to the entire room with turn information
                emit('move_made', {
                    'row': r, 
                    'column': column, 
                    'color': color, 
                    'turn': next_player_color
                }, to=room)

                # Check for winner
                if check_winner(board, color):
                    emit('game_over', {'winner': color}, to=room)
                return
        
        # If column is full, notify the player
        print(f"ERROR: Column {column} is full")
        emit('error', {'message': 'Column is full. Choose another column.'})
    else:
        # Not this player's turn
        print(f"ERROR: Not player's turn. Current turn is: {games[room]['turn']}")
        emit('error', {'message': f"It is not your turn. Current turn: {games[room]['player_colors'][games[room]['turn']]}"})

@socketio.on('rematch')
def rematch(data):
    """Handles a player's request for a rematch."""
    room = data['room']
    if room in games:
        # Notify the other player of the rematch request
        other_player_sid = next(p for p in games[room]['players'] if p != request.sid)
        emit('rematch_request', {'room': room}, to=other_player_sid)

@socketio.on('reset_game')
def reset_game(data):
    """Resets the game state for a rematch."""
    room = data['room']
    if room in games:
        # Reset the board
        games[room]['board'] = [['' for _ in range(7)] for _ in range(6)]
        # Reset the turn to the red player
        red_player_sid = [p for p, c in games[room]['player_colors'].items() if c == 'red'][0]
        games[room]['turn'] = red_player_sid
        # Notify both players that the game has been reset
        emit('game_reset', {'turn': 'red'}, to=room)

def check_winner(board, color):
    """Checks if the current player has won the game."""
    # Check horizontal
    for r in range(6):
        for c in range(4):
            if all(board[r][c+i] == color for i in range(4)):
                return True
    # Check vertical
    for r in range(3):
        for c in range(7):
            if all(board[r+i][c] == color for i in range(4)):
                return True
    # Check positively sloped diagonals
    for r in range(3):
        for c in range(4):
            if all(board[r+i][c+i] == color for i in range(4)):
                return True
    # Check negatively sloped diagonals
    for r in range(3, 6):
        for c in range(4):
            if all(board[r-i][c+i] == color for i in range(4)):
                return True
    return False

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
