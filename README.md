# bgp-streamer
quick and hacky socketsIO implementation for testing BGP streaming

## run

./streamer.py

Will attempt to connect to the streaming service.

## filter.json

The JSON blob within is sent to the server to filter only what we want. Only
one filter is supported right now. streamer.py will look at this file
frequently, and if the file changes it'll unsubscribe from the previous filter
and try to install the new one. This probably breaks in a ton of interesting
ways.

This makes it pretty easy though to drill down to, say, 1.0.0.0/8, or ::/0, or
all withdrawals, etc, etc.
