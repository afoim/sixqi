from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 游戏状态
class GameState:
    def __init__(self):
        self.board = [[0] * 19 for _ in range(19)]  # 0: 空, 1: 黑, 2: 白
        self.current_player = 1  # 1: 黑, 2: 白
        self.moves_count = 0
        self.players = {}
        self.game_started = False
        self.current_move_count = 0  # 当前玩家在这一轮已经下的子数

# 房间管理
class RoomManager:
    def __init__(self):
        self.rooms = defaultdict(GameState)
        self.player_room = {}

room_manager = RoomManager()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('create_room')
def handle_create_room(data):
    room_id = data.get('room_id')
    player_id = data.get('player_id')
    
    print(f'Creating room: {room_id} for player: {player_id}')
    
    if room_id in room_manager.rooms and len(room_manager.rooms[room_id].players) > 0:
        emit('room_exists', room=player_id)
        return
        
    join_room(room_id)
    room_manager.player_room[player_id] = room_id
    room_manager.rooms[room_id] = GameState()  # 创建新的游戏状态
    room_manager.rooms[room_id].players[player_id] = 1
    emit('room_created', {'room_id': room_id, 'player_number': 1})

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data.get('room_id')
    player_id = data.get('player_id')
    
    print(f'Joining room: {room_id} for player: {player_id}')
    
    if room_id in room_manager.rooms:
        game_state = room_manager.rooms[room_id]
        if len(game_state.players) < 2 and player_id not in game_state.players:
            join_room(room_id)
            room_manager.player_room[player_id] = room_id
            game_state.players[player_id] = 2
            emit('player_joined', {'player_number': 2})
            
            game_state.game_started = True
            emit('game_start', {'current_player': game_state.current_player}, room=room_id)
        else:
            emit('room_full')
    else:
        emit('room_not_found')

@socketio.on('move')
def handle_move(data):
    player_id = data.get('player_id')
    x = data.get('x')
    y = data.get('y')
    
    if player_id not in room_manager.player_room:
        return
        
    room_id = room_manager.player_room[player_id]
    game_state = room_manager.rooms[room_id]
    
    if not game_state.game_started:
        return

    if player_id not in game_state.players or game_state.players[player_id] != game_state.current_player:
        return

    if game_state.board[y][x] != 0:
        return

    game_state.board[y][x] = game_state.current_player
    game_state.moves_count += 1
    game_state.current_move_count += 1

    # 检查是否获胜
    win_line = check_win(game_state, x, y, game_state.current_player)
    if win_line:
        # 先发送棋子移动信息
        emit('move_made', {
            'x': x,
            'y': y,
            'player': game_state.players[player_id],
            'current_player': game_state.current_player,
            'moves_count': game_state.moves_count,
            'current_move_count': game_state.current_move_count
        }, room=room_id)
        
        emit('game_over', {
            'winner': game_state.current_player,
            'win_line': win_line
        }, room=room_id)
        room_manager.rooms[room_id] = GameState()
        return

    # 第一步黑棋只下一子，之后每步下两子
    next_player = game_state.current_player
    next_move_count = game_state.current_move_count
    
    if game_state.moves_count == 1:  # 黑棋第一步后切换到白棋
        next_player = 3 - game_state.current_player
        next_move_count = 0
    elif game_state.current_move_count == 2:  # 每个玩家下完两子后切换
        next_player = 3 - game_state.current_player
        next_move_count = 0

    # 发送棋子移动信息，包含更新后的状态
    emit('move_made', {
        'x': x,
        'y': y,
        'player': game_state.players[player_id],
        'current_player': next_player,
        'moves_count': game_state.moves_count,
        'current_move_count': next_move_count
    }, room=room_id)
    
    # 更新游戏状态
    game_state.current_player = next_player
    game_state.current_move_count = next_move_count

def check_win(game_state, x, y, player):
    directions = [(1,0), (0,1), (1,1), (1,-1)]  # 水平、垂直、对角线
    for dx, dy in directions:
        line_positions = [(x, y)]  # 包含当前落子位置
        
        # 正向检查
        tx, ty = x + dx, y + dy
        while 0 <= tx < 19 and 0 <= ty < 19 and game_state.board[ty][tx] == player:
            line_positions.append((tx, ty))
            tx, ty = tx + dx, ty + dy
            
        # 反向检查
        tx, ty = x - dx, y - dy
        while 0 <= tx < 19 and 0 <= ty < 19 and game_state.board[ty][tx] == player:
            line_positions.insert(0, (tx, ty))  # 插入到开头保持顺序
            tx, ty = tx - dx, ty - dy
            
        if len(line_positions) >= 6:
            return line_positions
    return None

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)