#!/usr/bin/python3
import requests
import websockets
import time
import asyncio
import json
from chess_data import *
from chess_player_data import sessid
session = requests.Session()
def json_str(data):
	return json.dumps(data, indent = 1, sort_keys = True)

def print_json(data): # passed as a dict, not string
	seperate()
	print(json.dumps(data, indent = 1, sort_keys = False))
	seperate()

def do_ping(extra_data = []):
	extra_data = extra_data + [get_connect_data()]
	#print_json(extra_data)
	r = session.post(post_connect, json = extra_data, headers = default_headers)
	#print_json(r.json())
	#update_connect_data(find_channel(r.json(), "/meta/connect")[0])
	return r.json()

def do_send_move(game_id, move, clock_time):
	data = get_send_move_data(game_id, move, clock_time)
	r = session.post(cometd, json = data, headers = default_headers)
	r.raise_for_status()
	return r.json()

def do_search_game():
	data = get_search_game_data()
	r = session.post(cometd, json = data, headers = default_headers)
	r.raise_for_status()
	return r.json()

def seperate(symb = "-"):
	print("\n" + symb * 20 + "\n")

def do_send_challenge_accept(c_id):
	r = session.post(cometd, json = get_challenge_accept(c_id), headers = default_headers)
	#r.raise_for_status()
	return r.json()

def do_login():
	global session
	session.cookies.set(domain = ".chess.com", name = "PHPSESSID", value = sessid)
	return;
	uagent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
	h0 = {
		"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
		"sec-fetch-dest" : "document",
		"sec-fetch-mode" : "navigate",
		"sec-fetch-site" : "none",
		"sec-fetch-user" : "?1",
		"upgrade-insecure-requests" : "1",
		"scheme" : "https",
		"authority" : "www.chess.com"
	}
	r = session.get(login, headers = h0)
	r.raise_for_status()
	#session.cookies.set(domain = ".chess.com", value = "6aa4ecfff89ca8d33b6917601dc736bf3f25ae79-1588718350-1800-AZqm70II0UjDnNUWdFmK59pgp4MOUszdXOokoS2TdLw7sWwfh4+kZ2mv0W1XuUwKwYsi+HlCkKKaHbdNncvWCpA=", name = "__cf_bm")
	# who needs regex when u have this shit
	token = r.text[r.text.index("id=\"_token\""):]
	token = token[token.index("value=\"") + len("value=\""):]
	token = token[:token.index("\"")]
	r = session.get("https://www.chess.com/callback/i18n/en_US?url=%2Flogin", headers = {"User-Agent" : uagent})
	r.raise_for_status()
	print ("r.text = \n" + r.text)
	h = {"Referer" : "https://www.chess.com/login",
		"Origin" : "https://www.chess.com",
		"Host" : "www.chess.com",
		"User-Agent" : uagent
	}
	print ("token = \"" + token + "\"")
	print (session.cookies)
	print (r.cookies)
	time.sleep(2)
	r = session.post(login_check, data = get_login_data(token), headers = h)
	print (r.text)
	r.raise_for_status()

def do_post_handshake():
	global session
	r = session.post(handshake, json = get_handshake_data())
	#print_json(r.json())
	handshake_reply = find_channel(r.json(), "/meta/handshake")[0]
	open("handshake_reply.txt", "w").write(json_str(r.json()))
	set_client_id(handshake_reply["clientId"])
	return r.json()
"""
def main():
	do_login()
	print_json(do_post_handshake())
	seperate()
	do_search_game()
	seperate()
	while True:
		do_ping()
		seperate()

#main()
"""
