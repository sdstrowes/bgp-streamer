#!/usr/bin/env python
import ris_streamer
import json

def process_msg( *msg ):
	print "WEEEE" + json.dumps( msg )

def main():
	ris_streamer.set_ris_message_listener( process_msg )
	print "aap"
	ris_streamer.run()
	print "beep"

if  __name__ =='__main__':
	main()


