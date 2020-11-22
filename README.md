# [Chess.com](https://www.chess.com/home) bot

First argument to `main.py` should be file like `login_data_example.json`,
honestly I'm not sure if you even need the username but it's
being mentioned in the sent requests so not providing a proper one
will either not work or crash the website.

(providing an username and password used to work but then it 
started asking for those verify-you're-human things so getting
the PHPSESSID was a workaround)

If you change some variable (in `main.py` I think) it will 
wait for an incoming challenge to your account and accept it
instead of searching for a random player.

This whole thing is a mess because I was reversing the website
while writing the code, honestly I have no idea how it still
works after like over a year, I figured they would have changed
the api or something.

I'll probably remake this cleanly in js with callbacks and an AI
instead of a bot when I feel like it.

Also crashes sometimes because (I think) I didn't get all
the moves correct and probably is againts the website rules lol 
