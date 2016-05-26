#!/usr/bin/env python

import getopt
import json
import logging
import sys

from base64 import b64decode
from gzip import GzipFile
from time import sleep

from _io import StringIO
from outputparser import parseLine
from outputparser import tagLine
from screeps.screeps import Connection
from settings import getSettings


class Output(object):
    def __init__(self, output_format):
        self.output_format = output_format

    def on_message(self, message):
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
                results = map(lambda x: '<type="result">' + x + '</type>',
                              results)
                stream = stream + results

            message_count = len(stream)

            if message_count > 0:
                # Make sure the delay doesn't cause an overlap into other ticks
                if settings.get('smooth_scroll', False):
                    message_delay = 0.2 / message_count
                    if message_delay > 0.07:
                        message_delay = 0.07
                else:
                    message_delay = 0.00001

                for line in stream:
                    if self.output_format == 'color':
                        line_parsed = parseLine(line)
                    elif self.output_format == 'json':
                        line_parsed = json.dumps(line)
                    else:
                        line_parsed = tagLine(line)

                    print(line_parsed)
                    sys.stdout.flush()
                    sleep(message_delay)  # sleep for smoother scrolling
            return
        else:
            if 'error' in data[1]:
                # line = '<'+data[1]['error']
                line = "<severity=\"5\" type=\"error\">" + data[1]['error'] + "</font>"  # noqa
                if self.output_format == 'color':
                    line_parsed = parseLine(line)
                elif self.output_format == 'json':
                    line_parsed = json.dumps(line)
                else:
                    line_parsed = tagLine(line)

                print(line_parsed)
                return
            else:
                print('undiscovered protocol feature')
                print(json.dumps(message))

        print('on_message', message)


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["ifile=", "ofile="])
    settings = getSettings()
    screepsconsole = Connection(
                         email=settings['screeps_username'],
                         password=settings['screeps_password'],
                         ptr=settings['screeps_ptr'])
    logging.getLogger('websocket').addHandler(logging.StreamHandler())

    output_format = 'log'
    if len(sys.argv) > 1:
        if sys.argv[1] == 'interactive':
            output_format = 'tag'
        if sys.argv[1] == 'json':
            output_format = 'json'

    output = Output(output_format)
    screepsconsole.startWebSocket(output.on_message)
