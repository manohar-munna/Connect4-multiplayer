from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key'
socketio = SocketIO(app, async_mode='eventlet')

# A dictionary to store the state of active games
games = {}

@app.route('/')
def index():
    """Serves the main game page."""
    return render_template('index.html')

def reset_game(room):
    """Resets the board and turn for a rematch."""
    games[room]['board'] = [['' for _ in range(7)] for _ in range(6)]
    games[room]['turn_sid'] = games[room]['players'][0] # Red always starts
    games[room]['rematch_requests'] = []

@socketio.on('create_game')
def create_game(data):
    room = data['room']
    player_sid = request.sid
    if room in games:
        emit('error', {'message': f'Game room "{room}" already exists.'})
        return

    join_room(room)
    games[room] = {
        'players': [player_sid],
        'board': [['' for _ in range(7)] for _ in range(6)],
        'turn_sid': player_sid,
        'rematch_requests': []
    }
    emit('game_created', {'room': room})

@socketio.on('join_game')
def join_game(data):
    room = data['room']
    player_sid = request.sid
    game = games.get(room)
    if not game or len(game['players']) >= 2:
        emit('error', {'message': f'Game room "{room}" is full or does not exist.'})
        return

    join_room(room)
    game['players'].append(player_sid)
    
    red_sid = game['players'][0]
    yellow_sid = game['players'][1]
    
    # Send a personalized start message to each player
    emit('start_game', {'color': 'red', 'turn': 'red'}, to=red_sid)
    emit('start_game', {'color': 'yellow', 'turn': 'red'}, to=yellow_sid)

@socketio.on('make_move')
def make_move(data):
    room = data['room']
    column = data['column']
    player_sid = request.sid
    game = games.get(room)

    if not game or game['turn_sid'] != player_sid:
        return # Ignore move if it's not their turn

    board = game['board']
    color = 'red' if player_sid == game['players'][0] else 'yellow'
    
    for r in range(5, -1, -1):
        if board[r][column] == '':
            board[r][column] = color
            
            game['turn_sid'] = game['players'][1] if player_sid == game['players'][0] else game['players'][0]
            next_turn_color = 'yellow' if color == 'red' else 'red'

            emit('move_made', {'row': r, 'column': column, 'color': color, 'turn': next_turn_color}, to=room)

            if check_winner(board, color):
                emit('game_over', {'winner': color}, to=room)
            return

@socketio.on('rematch_request')
def handle_rematch(data):
    room = data['room']
    player_sid = request.sid
    game = games.get(room)
    if not game or player_sid not in game['rematch_requests']:
        game['rematch_requests'].append(player_sid)
        # Notify other player
        other_player = next(p for p in game['players'] if p != player_sid)
        emit('opponent_wants_rematch', to=other_player)

    if len(game['rematch_requests']) == 2:
        reset_game(room)
        red_sid = game['players'][0]
        yellow_sid = game['players'][1]
        emit('start_game', {'color': 'red', 'turn': 'red'}, to=red_sid)
        emit('start_game', {'color': 'yellow', 'turn': 'red'}, to=yellow_sid)

@socketio.on('disconnect')
def handle_disconnect():
    player_sid = request.sid
    # Find which room the player was in
    for room, game_data in list(games.items()):
        if player_sid in game_data['players']:
            emit('player_disconnected', {'message': 'Your opponent has disconnected.'}, to=room)
            del games[room]
            break

def check_winner(board, color):
    # (Winner checking logic is unchanged)
    for r in range(6):
        for c in range(4):
            if all(board[r][c+i] == color for i in range(4)): return True
    for r in range(3):
        for c in range(7):
            if all(board[r+i][c] == color for i in range(4)): return True
    for r in range(3):
        for c in range(4):
            if all(board[r+i][c+i] == color for i in range(4)): return True
    for r in range(3, 6):
        for c in range(4):
            if all(board[r-i][c+i] == color for i in range(4)): return True
    return False

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
