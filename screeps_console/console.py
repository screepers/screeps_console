#!/usr/bin/env python

from base64 import b64decode
import getopt
import json
import logging
from outputparser import parseLine
from outputparser import tagLine
import screepsapi
from settings import getSettings
from time import sleep
import websocket
from StringIO import StringIO
import sys
import zlib


class ScreepsConsole(screepsapi.Socket):
    format = 'color'

    def set_subscriptions(self):
        self.subscribe_user('console')
        pass


    def on_close(self, ws):
        print "### closed ###"
        self.disconnect()


    def on_message(self, ws, message):
        if (message.startswith('auth ok')):
            ws.send('subscribe user:' + self.user_id + '/console')
            return

        if (message.startswith('time')):
            return

        if (message.startswith('gz')):
            try:
                decoded = b64decode(message[3:])
                message = zlib.decompress(decoded, 0)
            except:
                print("Unexpected error:", sys.exc_info())
                return

        data = json.loads(message)

        if 'shard' in data[1]:
            shard = data[1]['shard']
        else:
            shard = 'shard0'


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
                    message_delay = 0.2 / message_count
                    if message_delay > 0.07:
                        message_delay = 0.07
                else:
                    message_delay = 0.00001

                for line in stream:
                    if self.format == 'color':
                        line_parsed = '%s: %s' % (shard, parseLine(line))
                    elif self.format == 'json':
                        line_parsed = json.dumps({'line':line,'shard':shard})
                    else:
                        line_parsed = '%s: %s' % (shard, tagLine(line))

                    print line_parsed
                    sys.stdout.flush()
                    sleep(message_delay) # sleep for smoother scrolling
            return
        else:
            if 'error' in data[1]:
                #line = '<'+data[1]['error']
                line = "<severity=\"5\" type=\"error\">" + data[1]['error'] + "</font>"
                if self.format == 'color':
                    line_parsed = '%s: %s' % (shard, parseLine(line))
                elif self.format == 'json':
                    line_parsed = json.dumps({'line':line,'shard':shard})
                else:
                    line_parsed = '%s: %s' % (shard, tagLine(line))

                print line_parsed
                return
            else:
                print 'undiscovered protocol feature'
                print json.dumps(message)

        print('on_message', message)

    def start(self):
        self.connect()


if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "hi:o:",["ifile=","ofile="])
    settings = getSettings()
    screepsconsole = ScreepsConsole(user=settings['screeps_username'], password=settings['screeps_password'], ptr=settings['screeps_ptr'], host=settings['screeps_host'])

    if len(sys.argv) > 1:
        if sys.argv[1] == 'interactive':
            screepsconsole.format = 'tag'
        if sys.argv[1] == 'json':
            screepsconsole.format = 'json'

    screepsconsole.start()
