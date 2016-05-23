#!/usr/bin/env python

import colorama
from colorama import Fore, Back, Style
import json
import os
import re
from screeps import ScreepsConnection
from time import sleep
import websocket
import sys
import yaml

colorama.init()

class ScreepsConsole(object):

    def __init__(self, user, password, ptr=False):
        self.user = user
        self.password = password
        self.ptr = ptr

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

        SEVERITY_RE = re.compile(r'<.*severity="(\d)">')
        TAG_RE = re.compile(r'<[^>]+>')

        data = json.loads(message)

        if 'messages' in data[1]:
            if 'log' in data[1]['messages']:
                for line in data[1]['messages']['log']:

                    # Extract severity from html tag
                    try:
                        match_return = SEVERITY_RE.match(line)
                        groups = match_return.groups()
                        if len(groups) > 0:
                            severity = int(groups[0])
                        else:
                            severity = 3
                    except:
                        severity = 3

                    # Add color based on severity
                    if 'severity' not in locals():
                        severity = 3
                    if severity == 0:
                        color = Style.DIM + Fore.BLUE
                    elif severity == 1:
                        color = Style.NORMAL + Fore.BLUE
                    elif severity == 2:
                        color = Style.BRIGHT + Fore.BLUE
                    elif severity == 3:
                        color = Style.BRIGHT + Fore.WHITE
                    elif severity == 4:
                        color = Style.NORMAL + Fore.RED
                    elif severity == 5:
                        color = Style.BRIGHT + Fore.RED
                    else:
                        color = Style.NORMAL + Fore.RED


                    # Replace html tab entity with actual tabs
                    line = line.replace('&#09;', "\t")
                    print color + TAG_RE.sub('', line) + Style.RESET_ALL
                    sleep(0.02) # sleep for smoother scrolling
            return

        print('on_message', message)


    def connect(self):
        url = 'wss://screeps.com/socket/websocket'
        #websocket.enableTrace(True)
        ws = websocket.WebSocketApp(url=url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    on_open=self.on_open)
        ws.run_forever(ping_interval=1)

    def start(self):
        self.connect()



def getSettings():
    if not getSettings.settings:
        cwd = os.getcwd()
        path = cwd + '/.settings.yaml'
        if not os.path.isfile(path):
            print 'no settings file found'
            sys.exit(-1)
            return False
        with open(path, 'r') as f:
            getSettings.settings = yaml.load(f)
    return getSettings.settings
getSettings.settings = False


if __name__ == "__main__":
    settings = getSettings()
    screepsconsole = ScreepsConsole(user=settings['screeps_username'], password=settings['screeps_password'], ptr=settings['screeps_ptr'])
    screepsconsole.start()
