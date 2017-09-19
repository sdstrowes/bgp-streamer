#!/usr/bin/env python

import json
import signal
import threading
import time
import sys

from socketIO_client import SocketIO, LoggingNamespace

event = threading.Event()
lock = threading.Lock()
parameters = {}

listener_funcs = {} ## finds listeners
def set_ris_message_listener( func ):
	listener_funcs['ris_message'] = func

# socket.io callbacks:
def on_pong(*args):
	print 'pong', args

def on_reconnect():
	print 'reconnect'

def on_reconnect_error():
	print 'reconnect error'

def on_error(*args):
	print 'Error:', args

def on_ris_message(*msg):
	for update in msg:
		if update["type"] == "A":
			print "A",json.dumps(msg)
			#print str(update["timestamp"]), update["type"], update["prefix"], update["peer"], update["path"]
		elif update["type"] == "W":
			print "W",json.dumps(msg)
			#print str(update["timestamp"]), update["type"], update["prefix"], update["peer"]

# thread-safe interaction:
def store_parameters(p):
	lock.acquire()
	global parameters
	parameters = p
	lock.release()

def get_parameters():
	lock.acquire()
	global parameters
	p = parameters
	lock.release()
	return p

def sig_handler(signum, frame):
	event.set()

# message-handler thread:
def listener_thread():
	print >>sys.stderr, "Started listener"

	socket = SocketIO('http://stream-dev.ris.ripe.net/stream', 80, LoggingNamespace)

	#socket.on('pong', on_pong)
	socket.on('reconnecting', on_reconnect)
	socket.on('reconnect_error', on_reconnect_error)
	socket.on('error', on_error)

	if 'ris_message' in listener_funcs: #TODO check type
		socket.on('ris_message', listener_funcs['ris_message'])
	else:
		socket.on('ris_message', on_ris_message)

	# send ping
	#socket.emit('ping')
	current_parameters = get_parameters()
	socket.emit('ris_subscribe', current_parameters);

	running = True
	while running:
		if event.isSet():
			running = False

		p = get_parameters()
		if (p != current_parameters):
			socket.emit('ris_unsubscribe', current_parameters);
			current_parameters = p
			socket.emit('ris_subscribe',   current_parameters);

		socket.wait(0.1)

	socket.emit('ris_unsubscribe', current_parameters);

	socket.disconnect()
	print >>sys.stderr, "Exited listener"

def read_config_file():
	with open('filter.json') as json_data:
		p = json.load(json_data)
	return p

# config-watcher thread:
def config_reader():
	print >>sys.stderr, "Starting config reader"

	running = True
	while running:
		store_parameters(read_config_file())

		if event.isSet():
			running = False

		time.sleep(1)

	print "Exiting config reader"


# bootstrap
def run():
	signal.signal(signal.SIGINT, sig_handler)

	config_watcher  = threading.Thread(target=config_reader, args=())
	socket_listener = threading.Thread(target=listener_thread, args=())

	store_parameters(read_config_file())

	config_watcher.start()
	socket_listener.start()

	# wow threading in python is horrible
	while config_watcher.isAlive():
		config_watcher.join(timeout=1)

	while socket_listener.isAlive():
		socket_listener.join(timeout=1)

if  __name__ =='__main__':
	run()

