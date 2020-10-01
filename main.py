#!/usr/bin/python3
import time
from chess_connection import *
from chess_player import *
import sys
logfile = "logfile.txt"
def log(s, end = "\n"):
	with open(logfile, "a") as f:
		f.write(str(s) + end)

def tid_find(data, valid):
	ret = []
	for i in data:
		try:
			if i["data"]["tid"] in valid:
				ret.append(i)
		except KeyError:
			pass
	return ret

def log_invalid_move(s, end = "\n"):
	with open("invalid_moves.txt", "a") as f:
		f.write(str(s) + "\n")

def main():
	global _handshake_data
	wait_chally = False
	# change this if you want the account instead wait or accept an incoming match request
	# and play againts whoever sent it
	log("")
	log("STARTING")
	global game_id, clockstarted, movemade
	clockstarted = False
	movemade = None
	do_login()
	print ("logged in")
	handshake_data = do_post_handshake()
	_handshake_data = handshake_data
	old_game = tid_find(handshake_data, ["GameState"])
	#continued = False
	if wait_chally:
		challys = find_channel(handshake_data, "/service/game")[0]["data"]["challenges"]
		if len(challys) != 0:
			print_json(do_send_challenge_accept(challys[0]["id"]))
		else:
			print ("old challys empty")
			while True:
				data = do_ping()
				print_json(data)
				valid_data = tid_find(data, ["Challenge"])
				if len(valid_data) != 0:
					print_json(valid_data)
					print_json(do_send_challenge_accept(valid_data[0]["data"]["challenge"]["id"]))
					print ("got chally")
					break
	elif len(old_game) != 0:
		log("found old game")
		old_game_data = old_game[0]
		print_json(old_game_data)
		print ("old game found")
		if old_game_data["data"]["game"]["reason"] != "subscription":
			print ("reason not subscription...")
		elif old_game_data["data"]["game"]["status"] != "in_progress":
			print ("status not in progress...")
		else:
			clockstarted = True
			game_continue(old_game_data)
	else:
		log ("searching for game...")
		print_json(do_search_game())
		print ("searching for game...")
		while True:
			data = do_ping()
			print_json(data)
			game_data = find_channel(data, "/service/game")
			game_found = False
			for i in game_data:
				if i["data"]["tid"] == "ChallengeAccept":
					#game_id = str(i["data"]["challenge"]["id"])
					enemy_name = i["data"]["challenge"]["by"]
					game_found = True
					break
				if i["data"]["tid"] == "ChallengeFail":
					log("challenge fail, sleeping 1 and searching again...");
					print("challenge fail, searching again...");
					time.sleep(1)
					print_json(do_search_game())
			if game_found:
				break
		print ("Found game againts {}".format(enemy_name))
		log ("Found game againts {}".format(enemy_name))
		process_data(data)
	while True:
		data = do_ping()
		#print_json(data)
		process_data(data)
		sys.stdout.flush()

def process_data(data):
	global movemade, clockstarted, unprocessed_data
	valid_data = []
	data += unprocessed_data
	unprocessed_data = []
	valid_data = tid_find(data, ["GameState", "MoveFail", "EndGame"])
	for i in valid_data:
		if i["data"]["tid"] == "MoveFail":
			print ("your last move was illegal")
			log_invalid_move(board_str(True))
			log_invalid_move(board_str(False))
			undo_send_move_data()
			game_re_move()
			continue
		status = i["data"]["game"]["status"]
		print ("status - " + status)
		if i["data"]["tid"] == "EndGame":
			results = i["data"]["game"]["results"]
			clocks = i["data"]["game"]["clocks"]
			players = i["data"]["game"]["players"]
			ratings = i["data"]["ratings"]
			end_str = []
			log("GAME ENDED")
			for i in range(2):
				end_str.append("")
				end_str.append(players[i]["uid"] + ": ")
				end_str.append("clock - " + str(clocks[i]))
				end_str.append("result - " + str(results[i]))
				end_str.append("rating - " + str(ratings[i]))
			end_str = "\n".join(end_str)
			print (end_str)
			log(end_str)
			log("END")
			exit(0)
		reason = i["data"]["game"]["reason"]
		print ("reason - " + reason)
		print ("")
		if reason == "clockstarted":
			clockstarted = True
			game_init(i)
			if movemade != None:
				game_move(movemade)
				movemade = None
		elif reason == "movemade":
			if clockstarted:
				game_move(i)
			else:
				movemade = i
	
if __name__ == "__main__":
	main()


