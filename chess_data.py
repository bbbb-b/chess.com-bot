import time
import binascii
import random
import string
import json
import sys
#from chess_player_data import username, password
username = json.load(open(sys.argv[1]))["username"]
post_connect = "https://live2.chess.com/cometd/connect"
handshake = "https://live.chess.com/cometd/handshake"
login = "https://www.chess.com/login"
#login = "https://www.chess.com/login_and_go"
login_check = "https://www.chess.com/login_check"
cometd = "https://live2.chess.com/cometd"
connection_id = 0
default_headers = {
	"content-type" : "application/json;charset=UTF-8",
	"Host" : "live2.chess.com",
	"Origin" : "https://www.chess.com",
	"Referer" : "https://www.chess.com/live",
}

challenge_accept = {
	"channel" : "/service/game",
	"clientId" : "",
	"data" : {
		"id" : "##",
		"sid" : "gserv",
		"tid" : "ChallengeAccept"
	},
	"id" : "##"
}
# 56622410

send_move_data = {
	"channel" : "/service/game",
	"clientId" : "",
	"data" : {
		"move" : {
			"clock" : "##",
			"clickms" : "##",
			"coh" : True, # ???
			"gid" : "##",
			"lastmovemessagesent" : False,    # ??? always false
			"mht" : 1000,
			"move" : "##",
			"seq" : -2,
			"squared" : True,   # ???
			"uid" : username
		},
		"sid" : "gserv",
		"tid" : "Move"
	},
	"id" : "##"
}


search_game_data = {
	"channel" : "/service/game",
	"data" : {
		"basetime" : 600, # minutes * 60 * 10
		"timeinc" : 0,
		"uuid" : "db75e6d",  #  7 chars long random id of lower case and nums
		"from" : username,
		"gametype" : "chess",
		"rated" : True,
		"minrating" : 1000,
		"maxrating" : 1500,
		"sid" : "gserv", # ??
		"tid" : "Challenge"
	},
	"id" : "##",
	"clientId" : ""
}

"""
login_data = {
	"_username" : username,
	"_password" : password,
	"login" : "",
	"_target_path" : "https://www.chess.com/home",
	"_token" : ""
}
"""
# ^ this isnt used when connecting with phpsessid

handshake_data = {
	"version" : "1.0",
	"minimumVersion" : "1.0",
	"channel" : "/meta/handshake",
	"supportedConnectionTypes" : [ "ssl-long-polling" ],
	"advice" : {
		"timeout" : 60000,
		"interval" : 0
	},
	"clientFeatures" : {
		"protocolversion" : "2.1",
		"clientname" : "4chan",
		"clientenvironment" : "prod",
		"adminservice" : True,
		"announceservice" : True,
		"arenas" : True,
		"chessgroups" : True,
		"events" : True,
		"examineboards" : True,
		"gameobserve" : True,
		"genericchatsupport" : True,
		"genericgamesupport" : True,
		"guessthemove" : True,
		"multiplegames" : True,
		"multiplegamesobserve" : True,
		"pingservice" : True,
		"playbughouse" : True,
		"playchess" : True,
		"playchess960" : True,
		"playcrazyhouse" : True,
		"playkingofthehill" : True,
		"playoddchess" : True,
		"playthreecheck" : True,
		"privatechats" : True,
		"stillthere" : True,
		"teammatches" : True,
		"tournaments" : True,
		"userservice" : True,
		"offlinechallenges" : True
	},
	"serviceChannels" : [ "/service/user" ],
	"options" : [],
	"ext" : {
		"ack" : True,
		"timesync" : {
			"tc" : round(time.time() * 1e3),
			"l" : 0,
			"o" : 0
		}
	},
	"id" : "##",
	"clientId" : None
}

connect_data = {
	"channel" : "/meta/connect",
	"connectionType" : "auto",
	"ext" : {
		"ack" : 0,
		"timesync" : {
			"tc" : round(time.time() * 1e3),
			"l" : 300,
			"o" : -325
			}
		},
	"id" : "##",
	"clientId" : ""
}

def init_send_move_data(seq):
	send_move_data["data"]["move"]["seq"] = seq - 2


def get_send_move_data(game_id, move, clock_time):
	send_move_data["id"] = next_id()
	send_move_data["data"]["move"]["clock"] = clock_time
	send_move_data["data"]["move"]["clockms"] = int(clock_time * 100)
	send_move_data["data"]["move"]["gid"] = game_id
	send_move_data["data"]["move"]["move"] = move
	send_move_data["data"]["move"]["seq"] += 2
	return send_move_data

def undo_send_move_data():
	send_move_data["data"]["move"]["seq"] -= 2

def get_random_uuid(sz):
	return "".join(random.choice(string.ascii_letters + string.digits) for _ in range (sz))

def next_id():
	global connection_id
	connection_id += 1
	return str(connection_id)

def find_channel(server_data, channel_name):
	ret = []
	for i in server_data:
		if i["channel"] == channel_name:
			ret.append(i)
		else:
			continue
			print("invalid channel - " + i["channel"])
			print("target channel - " + channel_name)
			print (binascii.hexlify(i["channel"].encode()))
			print (binascii.hexlify(channel_name.encode()))

	return ret

def get_challenge_accept(c_id):
	challenge_accept["id"] = next_id()
	challenge_accept["data"]["id"] = c_id
	return challenge_accept

def set_client_id(clientId):
	connect_data["clientId"] = clientId
	search_game_data["clientId"] = clientId
	send_move_data["clientId"] = clientId
	challenge_accept["clientId"] = clientId

def get_login_data(token):
	login_data["_token"] = token
	return login_data

def get_handshake_data():
	handshake_data["id"] = next_id()	
	handshake_data["ext"]["timesync"]["tc"] = round(time.time() * 1e3)
	return handshake_data

def get_connect_data():
	connect_data["ext"]["ack"] += 1
	connect_data["id"] = next_id()
	connect_data["ext"]["timesync"]["tc"] = round(time.time() * 1e3)
	return connect_data
	
def update_connect_data(connect_response):
	connect_data["ext"]["timesync"]["o"] = connect_response["ext"]["timesync"]["ts"] - connect_response["ext"]["timesync"]["tc"]

def get_search_game_data():
	search_game_data["id"] = next_id()
	search_game_data["data"]["uuid"] = get_random_uuid(7)
	return search_game_data

