# SAChat v 1.0

#1. Introduction

The SAChat is a chat that analyses your emotions.You simply chat with your friends and the SAChat maytell you how you and your friends are feeling at the moment.
SAChat uses DepecheMood emotion lexicon to get the scores for each word. It contains more than 37k words. More details at http://www.depechemood.eu/DepecheMood.html.

#2. Usage
First you need to start the server. Simply go to Server folder and type
	python Server.py ip port

where ip is the ip address on which the server shall listen and port the port on which you wish to start listening.

Then you can open the chat. Here one can type

	#help

to see the available commands, but i will explain the ones you need to connect here.

First you must also set a listening interface for the chat. The command is

	#listen ip port

The ip and port  meanings are the same as for Server. On this interface you shall receive the messages.

Now you are ready to connect to the server. Type

	#register nick ip port

where nick is the nickname you want to use. User nicknames must not be the same in the same chat room. The ip and port are the ones you earlier set for
the server. Now you have a fully working emotion analyising chat. Enjoy!

#3. Dependecies

What you need for the chat to work is:

a) qtcore for the graphical interface;

b) nltk library for python; you must download english.pickle corpus from there;

The chat it's in initial version so bugs may appear. Future improvements shall be made!
ENJOY!
