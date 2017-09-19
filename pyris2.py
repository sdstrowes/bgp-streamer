#!/usr/bin/env python

### find interesting events from RIS stream, using minimal set of peers

import json
import signal
import threading
import time
import sys

from socketIO_client import SocketIO, LoggingNamespace


#### config
#TODO select better ones
peer_set = set([
	"91.206.52.60",
	"37.49.236.228",
   "196.60.8.215"
])

# socket.io callbacks:
def on_pong( *args ):
	print >>sys.stderr, 'pong', args

def on_reconnect():
	print >>sys.stderr, 'reconnect'

def on_reconnect_error():
	print >>sys.stderr, 'reconnect error'

def on_error( *args ):
	print >>sys.stderr, 'Error:', args

data = {
	'm_counter': 0,
	'counter': 0,
}

def on_msg( *msg ):
	for update in msg:
		#if update["type"] == "W" and update["peer"] in peer_set:
		if update["peer"] in peer_set and update["type"] == "W":
			data['m_counter'] += 1
			#print str(update["timestamp"]), update["type"], update["prefix"], update["peer"], update["path"]
		data['counter'] += 1
		if not data['counter'] % 1000:
			print "%.7f %s" % ( data['m_counter']*1.0/data['counter'], data['counter'] )

def run():
	socket = SocketIO('http://stream-dev.ris.ripe.net/stream', 80, LoggingNamespace)
	print >>sys.stderr, "Started listener"

	#socket.on('pong', on_pong)
	socket.on('reconnecting', on_reconnect)
	socket.on('reconnect_error', on_reconnect_error)
	socket.on('error', on_error)
	socket.on('ris_message', on_msg)
	socket.emit('ris_subscribe', {})
	#TODO get filtering upstream going
	#socket.emit('ris_subscribe', json.loads('{"peer":"196.60.8.60"}')) # angola cables RRC19 SA
	#socket.emit('ris_subscribe', json.loads('{"peer":"193.242.98.141"}')) # voz telecom RRC18 CATALUNIA
	#socket.emit('ris_subscribe', json.loads('{"peer":"37.49.236.246"}' )) # WIL @ RRC21 FRANCE-IX
	print >>sys.stderr, "listener set!"
	while 1:
		socket.wait(0.1)

if  __name__ =='__main__':
	run()

