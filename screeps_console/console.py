#!/usr/bin/env python

from base64 import b64decode
import getopt
from gzip import GzipFile
import json
import logging
from outputparser import parseLine
from outputparser import tagLine
from screeps import ScreepsConnection
from settings import getSettings
from time import sleep
import websocket
import sys


class ScreepsConsole(object):

    def __init__(self, user, password, ptr=False, logging=False):
        self.format = 'color'
        self.user = user
        self.password = password
        self.ptr = ptr
        self.logging = False

    def on_message(self, ws, message):
        print message

    def on_error(self, ws, error):
        print error

    def on_close(self, ws):
        print "### closed ###"

    def on_open(self, ws):
        screepsConnection = ScreepsConnection(u=self.user,p=self.password,ptr=self.ptr)
        me = screepsConnection.me()
        self.user_id = me['_id']
        ws.send('auth ' + screepsConnection.token)


    def on_message(self, ws, message):

        if (message.startswith('auth ok')):
            ws.send('subscribe user:' + self.user_id + '/console')
            return

        if (message.startswith('time')):
            return

        if (message.startswith('gz')):
            message = GzipFile(fileobj=StringIO(b64decode(message[3:])))

        data = json.loads(message)

        if 'messages' in data[1]:
            stream = []

            if 'log' in data[1]['messages']:
                stream = stream + data[1]['messages']['log']

            if 'results' in data[1]['messages']:
                results = data[1]['messages']['results']
                results = map(lambda x:'<type="result">'+x+'</type>',results)
                stream = stream + results


            message_count = len(stream)

            if message_count > 0:
                # Make sure the delay doesn't cause an overlap into other ticks
                if 'smooth_scroll' in settings and settings['smooth_scroll'] is True:
                    message_delay = 0.3 / message_count
                    if message_delay > 0.10:
                        message_delay = 0.10
                else:
                    message_delay = 0.00001

                for line in stream:
                    if self.format == 'color':
                        line_parsed = parseLine(line)
                    elif self.format == 'json':
                        line_parsed = json.dumps(line)
                    else:
                        line_parsed = tagLine(line)

                    print line_parsed
                    sys.stdout.flush()
                    sleep(message_delay) # sleep for smoother scrolling
            return
        else:
            if 'error' in data[1]:
                #line = '<'+data[1]['error']
                line = "<severity=\"5\" type=\"error\">" + data[1]['error'] + "</font>"
                if self.format == 'color':
                    line_parsed = parseLine(line)
                elif self.format == 'json':
                    line_parsed = json.dumps(line)
                else:
                    line_parsed = tagLine(line)

                print line_parsed
                return
            else:
                print 'undiscovered protocol feature'
                print json.dumps(message)

        print('on_message', message)


    def connect(self):

        if self.logging:
            logging.getLogger('websocket').addHandler(logging.StreamHandler())
            websocket.enableTrace(True)
        else:
            logging.getLogger('websocket').addHandler(logging.NullHandler())
            websocket.enableTrace(False)

        if not self.ptr:
            url = 'wss://screeps.com/socket/websocket'
        else:
            url = 'wss://screeps.com/ptr/socket/websocket'

        ws = websocket.WebSocketApp(url=url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    on_open=self.on_open)
        if 'http_proxy' in settings and settings['http_proxy'] is not None:
            http_proxy_port = settings['http_proxy_port'] if 'http_proxy_port' in settings else 8080
            ws.run_forever(http_proxy_host=settings['http_proxy'], http_proxy_port=http_proxy_port, ping_interval=1)
        else:
            ws.run_forever(ping_interval=1)

    def start(self):
        self.connect()


if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "hi:o:",["ifile=","ofile="])
    settings = getSettings()
    screepsconsole = ScreepsConsole(user=settings['screeps_username'], password=settings['screeps_password'], ptr=settings['screeps_ptr'])

    if len(sys.argv) > 1:
        if sys.argv[1] == 'interactive':
            screepsconsole.format = 'tag'
        if sys.argv[1] == 'json':
            screepsconsole.format = 'json'

    screepsconsole.start()
