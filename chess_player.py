#!/usr/bin/python3
from chess_connection import *
import select
import sys
from pwn import process
from main import log
turn_queen_normal = "~"
turn_queen_left = "}"
turn_queen_right = "{"

turn_knight_normal = "^"
turn_knight_left = ")"
turn_knight_right = "("

turn_rook_normal = "_"
turn_rook_left = "]"
turn_rook_right = "["

turn_bishop_normal = "#"
turn_bishop_left = "$"
turn_bishop_right = "@"

KING = 6
QUEEN = 5
ROOK = 4
BISHOP = 3
KNIGHT = 2
PAWN = 1
KING_ASCII = "K"
QUEEN_ASCII = "Q"
ROOK_ASCII = "r"
BISHOP_ASCII = "b"
KNIGHT_ASCII = "k"
PAWN_ASCII = "p"
# as_white
position_board = [
	"456789!?",
	"WXYZ0123",
	"OPQRSTUV",
	"GHIJKLMN",
	"yzABCDEF",
	"qrstuvwx",
	"ijklmnop",
	"abcdefgh"
]

def init_game_data():
	global game_board, ascii_translate
	game_board = []
	game_board.append([-ROOK, -KNIGHT, -BISHOP, -QUEEN, -KING, -BISHOP , -KNIGHT, -ROOK])
	game_board.append([-PAWN] * 8)
	for _ in range(4):
		game_board.append([0] * 8)
	game_board.append([PAWN] * 8)
	game_board.append([ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP , KNIGHT, ROOK])
	ascii_translate = {}
	tmp = ["", PAWN_ASCII, KNIGHT_ASCII, BISHOP_ASCII, ROOK_ASCII, QUEEN_ASCII, KING_ASCII]
	for i in range(1, len(tmp)):
		ascii_translate[i] = "+" + tmp[i]
		ascii_translate[-i] = "-" + tmp[i]
	ascii_translate[0] = "  "
	return

"""
board is as
   (1, 2, 3...)
 A
 B
 C
 ...
"""
unprocessed_data = []
local_run = False
def slow_input(fd):
	global unprocessed_data
	while True:
		tmp = select.select([fd], [], [], 7)[0]
		if len(tmp) != 0:
			return fd.readline().strip().decode()
		print (" (7 seconds passed, waiting...) ")
		if not local_run:
			unprocessed_data += do_ping()


def str_to_yx(string):
	for y in range(8):
		for x in range(8):
			if position_board[y][x] == string:
				return (y, x)
	
def valid_move(string):
	# good example = "a1b3"
	if len(string) != 4:
		print ("invalid move - string size invalid") 
		return None
	# as (y, x)
	_from = (ord(string[0]) - ord('a'), ord(string[1]) - ord('1'))
	_to   = (ord(string[2]) - ord('a'), ord(string[3]) - ord('1'))
	print ("from = " + str(_from))
	print ("to   = " + str(_to))
	valid = range(0, 8)
	if not ((_from[0] in valid) and (_from[1] in valid)):
		print ("invalid move - from characters invalid")
		return None
	if not ((_to[0] in valid) and (_to[1] in valid)):
		print ("invalid move - to charaters invalid")
		return None

	ret = position_board[_from[0]][_from[1]]
	if game_board[_from[0]][_from[1]] == PAWN and (_to[0] == 0 or _to[0] == 7): #y is 0 or 7
		diff = _from[1] - _to[1] # diff from x
		if diff == -1:
			ret += turn_queen_right
		elif diff == 0:
			ret += turn_queen_normal
		elif diff == 1:
			ret += turn_queen_left
		else:
			log("invalid turn queen ??")
			print("invalid turn queen ??")
	else:
		ret += position_board[_to[0]][_to[1]]
	return ret

def board_str(pretty = False):
	ret = ""
	if pretty:
		ret += " " * 4
		for x in range(8):
			ret += "(#" + str(x+1) + ") "
		ret += "\n"
		for y in range(8):
			ret += "(" + chr(y + ord("A")) + ") "
			for x in range(8):
				ret += "[" + ascii_translate[game_board[y][x]] + "] "
			ret += "\n"
	else:
		for y in range(8):
			for x in range(8):
				ret += str(game_board[y][x] * playing_as) + " "
			ret += "\n"
	return ret

def get_move_player():
	while True:
		mv = valid_move(slow_input(sys.stdin))
		if mv != None:
			break
	return mv
		
def get_move_bot():
	stime = time.time()
	p = process("./cpplayer", stderr = sys.stderr)
	p.send(board_str(False))
	ret = slow_input(p.stdout)
	#ret = p.recvline().strip().decode()
	p.kill()
	print ("bot move - " + ret)
	etime = time.time()
	print ("took {:.6f} seconds for bot to move".format(etime-stime))
	ret = valid_move(ret)
	if ret == None:
		print ("invalid bot move")
		exit(1)
	return ret

def register_move(clock_time):
	print ("friendly reminder that youre playing as " + ("minuses" if playing_as == -1 else "pluses"))
	print (board_str(True))
	print (board_str(False))
	mv = get_move_bot()
	print ("your move - " + mv)
	print_json(do_send_move(game_id, mv, clock_time))
	print ("waiting for enemy move...")


def invert(_board):
	return (list(map(lambda x : x[::-1], _board))[::-1])

def get_playing_as():
	return playing_as
def game_continue(data):
	global position_board, game_board, playing_as
	global game_id, last_data
	last_data = data
	init_game_data()
	game_id = data["data"]["game"]["id"]
	seq = data["data"]["game"]["seq"]
	# seq means the next message should send seq so if its 0, means its whites turn cuz white starts
	if data["data"]["game"]["players"][0]["uid"] != username:
		position_board = invert(position_board)
		game_board = invert(game_board)
		playing_as = -1
		my_turn = seq % 2 == 1
		print ("playing as blacks")
	else:
		playing_as = 1
		my_turn = seq % 2 == 0
		print ("playing as whites")
	init_send_move_data(seq + (0 if my_turn else 1))
	for i in range(0, len(data["data"]["game"]["moves"]), 2):
		board_move(data["data"]["game"]["moves"][i:i+2])
	if my_turn:
		register_move(data["data"]["game"]["clocks"][0 if playing_as == 1 else 1])



def game_init(data):
	global position_board, game_board, playing_as
	global game_id, last_data
	last_data = data
	init_game_data()
	game_id = data["data"]["game"]["id"]
	if data["data"]["game"]["players"][0]["uid"] != username:
		position_board = invert(position_board)
		game_board = invert(game_board)
		playing_as = -1
		init_send_move_data(1)
		print ("playing as blacks")
	else:
		playing_as = 1
		init_send_move_data(0)
		print ("playing as whites")
	if (playing_as == 1):
		register_move(data["data"]["game"]["clocks"][0])


def game_re_move():
	clock = last_data["data"]["game"]["clocks"][0 if playing_as == 1 else 1]
	register_move(clock)

def board_quick_move(_from, _to):
	global game_board
	if game_board == None:
		print ("gameboard is none")
	if game_board[_to[0]] == None:
		print ("gameboard[] is none")
	game_board[_to[0]][_to[1]] = game_board[_from[0]][_from[1]]
	game_board[_from[0]][_from[1]] = 0


def board_move(string):
	global game_board
	# y, x
	_from = str_to_yx(string[0])
	_to   = str_to_yx(string[1])
	move_side = -playing_as if game_board[_from[0]][_from[1]] < 0 else playing_as
	# if 1 if its the same as mine, else -1
	if _to == None: 
		if string[1] == turn_queen_normal:
			_to = (_from[0]-move_side, _from[1])
			game_board[_from[0]][_from[1]] = QUEEN * move_side * playing_as
		elif string[1] == turn_queen_left:
			_to = (_from[0]-move_side, _from[1]-move_side)
			game_board[_from[0]][_from[1]] = QUEEN * move_side * playing_as
		elif string[1] == turn_queen_right:
			_to = (_from[0]-move_side, _from[1]+move_side)
			game_board[_from[0]][_from[1]] = QUEEN * move_side * playing_as
		else:
			log("someone choose to not take queen" + string)
			print("someone choose to not take queen" + string)
	if abs(game_board[_from[0]][_from[1]]) == KING:
		if abs(_to[1] - _from[1]) == 2:
			sgn = -1 if (_to[1] - _from[1]) < 0 else 1
			if _to[1] <= 2:
				_from_y = 0
			elif 5 <= _to[1]:	
				_from_y = 7
			board_quick_move((_to[0], _from_y), (_to[0], _to[1]-sgn))
			
	board_quick_move(_from, _to)

def game_move(data):
	global last_data, game_board
	last_data = data
	my_move = False
	tmp = (len(data["data"]["game"]["moves"]) / 2) % 2
	if (playing_as == 1 and tmp == 1) or (playing_as == -1 and tmp == 0):
		my_move = True
	board_move(data["data"]["game"]["moves"][-2] + data["data"]["game"]["moves"][-1])
	clock = data["data"]["game"]["clocks"][0 if playing_as == 1 else 1]
	if not my_move:
		register_move(clock)
	print(board_str(True))

def pmain(): # local play
	init_game_data()
	global position_board, game_board, local_run, playing_as
	local_run = True
	playing_as = -1
	position_board = invert(position_board)
	game_board = invert(game_board)
	while True:
		print ("pluses")
		print (board_str(True), end = "")
		print (board_str(False), end = "")
		b_move = get_move_bot()
		board_move(b_move)
		print ("minuses")
		print (board_str(True), end = "")
		print (board_str(False), end = "")
		p_move = get_move_player()
		board_move(p_move)

if __name__ == "__main__":
	pmain()


