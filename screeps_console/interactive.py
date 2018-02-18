#!/usr/bin/env python

import atexit
import command
import json
import logging
import os
from os.path import expanduser
import outputparser
import re
import settings
import signal
import subprocess
import sys
from themes import themes
import urwid

if hasattr(__builtins__, 'raw_input'):
    input = raw_input

class ScreepsInteractiveConsole:

    consoleWidget = False
    listWalker = False
    userInput = False
    consoleMonitor = False

    def __init__(self, connection_name):
        try:
            self.connection_name = connection_name
            frame = self.getFrame()
            comp = self.getCommandProcessor()
            self.loop = urwid.MainLoop(urwid.AttrMap(frame, 'bg'),
                                        unhandled_input=comp.onInput,
                                        palette=themes['dark'])

            self.consoleMonitor = ScreepsConsoleMonitor(connection_name,
                                                        self.consoleWidget,
                                                        self.listWalker,
                                                        self.loop)

            comp.setDisplayWidgets(self.loop,
                                   frame,
                                   self.getConsole(),
                                   self.getConsoleListWalker(),
                                   self.getEdit(),
                                   self.consoleMonitor)
            self.loop.run()
        except KeyboardInterrupt:
            exit(0)


    def getFrame(self):
        urwid.AttrMap(self.getEdit(), 'input')
        frame_widget = urwid.Frame(
            header=self.getHeader(),
            body=self.getConsole(),
            footer=urwid.AttrMap(self.getEdit(), 'input'),
            focus_part='footer')
        return frame_widget


    def getHeader(self):
        return urwid.AttrMap(urwid.Text("%s - Screeps Interactive Console" % (self.connection_name,), align='center'), 'header')

    def getEdit(self):
        if not self.userInput:
            self.userInput = consoleEdit("> ")
        return self.userInput

    def getConsole(self):
        if not self.consoleWidget:
            self.consoleWidget = consoleWidget(self.getConsoleListWalker())
        return self.consoleWidget

    def getConsoleListWalker(self):
        if not self.listWalker:
            self.listWalker = consoleWalker([self.getWelcomeMessage()])
            config = settings.getSettings()
            if 'max_buffer' in config:
                self.listWalker.max_buffer = config['max_buffer']
            else:
                self.listWalker.max_buffer = 200000

        return self.listWalker

    def getCommandProcessor(self):
        return command.Processor(self.connection_name)

    def getWelcomeMessage(self):
        return urwid.Text(('default', 'Welcome to the Screeps Interactive Console'))


class consoleWidget(urwid.ListBox):

    _autoscroll = True


    def setAutoscroll(self, option):
        self._autoscroll = option


    def autoscroll(self):
        if(self._autoscroll):
            self.scrollBottom()

    def scrollBottom(self):
        self._autoscroll = True
        if len(self.body) > 0:
            self.set_focus(len(self.body)-1)

    def scrollUp(self, quantity):
        self.setAutoscroll(False)
        new_pos = self.focus_position - quantity
        if new_pos < 0:
            new_pos = 0
        self.set_focus(new_pos)


    def scrollDown(self, quantity):
        self.setAutoscroll(False)
        max_pos = len(self.body)-1
        new_pos = self.focus_position + quantity
        if new_pos > max_pos:
            self.setAutoscroll(True)
            new_pos = max_pos
        self.set_focus(new_pos)



class consoleWalker(urwid.SimpleListWalker):

    def appendText(self, message, format='logged_response'):
        self.append(urwid.Text((format, message)))

    def append(self, value):
        if(len(self) >= self.max_buffer):
            self.pop(0)

        return super(consoleWalker, self).append(value)


class consoleEdit(urwid.Edit):

    inputBuffer = []
    inputOffset = 0

    def __init__(self, caption=u'', edit_text=u'', multiline=False, align='left', wrap='space', allow_tab=False, edit_pos=None, layout=None, mask=None):
        path = expanduser('~') + '/.screeps_history'
        if os.path.isfile(path):
            with open(path, 'r') as myfile:
                file_contents = myfile.read()
                self.inputBuffer = file_contents.splitlines()
                self.inputBuffer.reverse()

        return super(consoleEdit, self).__init__(caption, edit_text, multiline, align, wrap, allow_tab, edit_pos, layout, mask)

    def bufferInput(self, text):
        if len(text) < 1:
            return
        path = expanduser('~') + '/.screeps_history'
        history_file = open(path, 'a')
        history_file.write(text + "\n")
        self.inputBuffer.insert(0, text)
        self.manageBufferHistory()

    def manageBufferHistory(self):
        path = expanduser('~') + '/.screeps_history'
        with open(path, 'r') as myfile:
            file_contents = myfile.read()
            file_contents_line = file_contents.splitlines()
            num_lines = len(file_contents_line)
            config = settings.getSettings()
            if 'max_history' in config:
                max_scroll = config['max_history']
            else:
                max_scroll = 200000

            if num_lines > max_scroll:
                truncate = num_lines - max_scroll
                list_copy = file_contents_line[:]
                list_copy = [s + "\n" for s in list_copy]
                open(path, 'w').writelines(list_copy[truncate+1:])

    def keypress(self, size, key):

        if key == 'enter':
            edit_text = self.get_edit_text()
            self.bufferInput(edit_text)
            self.inputOffset = 0
            return super(consoleEdit, self).keypress(size, key)

        if key == 'ctrl a':
            self.edit_pos = 0
            return

        if key == 'ctrl e':
            edit_text = self.get_edit_text()
            self.edit_pos = len(edit_text)
            return

        if key == 'ctrl u':
            self.set_edit_text('')
            self.edit_pos = 0
            return

        if key == 'up':
            bufferLength = len(self.inputBuffer)
            if bufferLength > 0:
                self.inputOffset += 1
                if self.inputOffset > bufferLength:
                    self.inputOffset = bufferLength

                index = self.inputOffset-1
                new_text = self.inputBuffer[index]
                self.set_edit_text(new_text)
                self.edit_pos = len(new_text)
            return

        if key == 'down':
            bufferLength = len(self.inputBuffer)
            if bufferLength > 0:
                self.inputOffset -= 1
                if self.inputOffset < 0:
                    self.inputOffset = 0

                if self.inputOffset == 0:
                    new_text = ''
                else:
                    index = self.inputOffset-1
                    new_text = self.inputBuffer[index]

                self.set_edit_text(new_text)
                self.edit_pos = len(new_text)
            return

        return super(consoleEdit, self).keypress(size, key)


class ScreepsConsoleMonitor:

    proc = False
    quiet = False
    focus = False
    filters = []

    def __init__(self, connectionname, widget, walker, loop):
        self.connectionname = connectionname
        self.widget = widget
        self.walker = walker
        self.loop = loop
        self.buffer = ''
        self.getProcess()
        atexit.register(self.__del__)

    def getProcess(self):
        if self.proc:
            return self.proc
        console_path = os.path.join(os.path.dirname(sys.argv[0]), 'console.py ')
        write_fd = self.loop.watch_pipe(self.onUpdate)
        self.proc = subprocess.Popen(
            [sys.executable + ' ' + console_path + ' ' + self.connectionname + ' json'],
            stdout=write_fd,
            preexec_fn=os.setsid,
            close_fds=True,
            shell=True)
        return self.proc


    def reconnect(self):
        self.disconnect()
        self.getProcess()

    def disconnect(self):
        if self.proc:
            try:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            except:
                pass
            self.proc = False

    def onUpdate(self, data):
        # If we lose the connection to the remote system close the console.
        if data.startswith(b'### closed ###'):
            self.proc = False
            self.getProcess()
            lostprocess_message = 'reconnecting to server . . .'
            self.walker.append(urwid.Text(('logged_response', lostprocess_message)))
            self.widget.set_focus(len(self.walker)-1)
            return
        if data[-1:] != b'\n':
            self.buffer += data.decode("utf-8")
            return
        if len(self.buffer) > 0:
            data = self.buffer + data.decode("utf-8")
            self.buffer = ''
        data_lines = data.decode("utf-8").rstrip().split('\n')
        for line_json in data_lines:
            try:
                if len(line_json) <= 0:
                    continue
                try:
                    line_data = json.loads(line_json.strip())
                    line = line_data['line']
                    shard = line_data['shard']

                    if self.focus and self.focus != line_data['shard']:
                        continue


                except:
                    print(line_json)
                    logging.exception('error processing data: ' + line_json)
                    continue

                log_type = outputparser.getType(line)

                if self.quiet and log_type != 'result':
                    return

                if log_type == 'result':
                    formatting = 'logged_response'
                elif log_type == 'highlight':
                    formatting = 'highlight'
                elif log_type == 'error':
                    formatting = 'error'
                else:
                    severity = outputparser.getSeverity(line)
                    if not severity or severity > 5 or severity < 0:
                        severity = 2
                    formatting = 'severity' + str(severity)

                line = line.replace('&#09;', " ")
                line = outputparser.clearTags(line)

                if line.startswith('ScreepStats: Processed'):
                    return
                
                if line.startswith('STATS'):
                    return

                if log_type == 'log' and len(self.filters) > 0:
                    has_match = False

                    for pattern in self.filters:
                        try:
                            match = re.search(pattern, line)
                        except:
                            e = sys.exc_info()[0]
                            logging.exception('dammit')

                        if match is not None:
                            has_match = True
                            break

                    if not has_match:
                        continue

                self.walker.append(urwid.Text((formatting, '%s: %s' % (shard, line))))
                self.widget.autoscroll()

            except:
                logging.exception('error processing data')

    def __del__(self):
        if self.proc:
            try:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            except:
                pass


if __name__ == "__main__":

    if len(sys.argv) < 2:
        server = 'main'
    else:
        server = sys.argv[1]

    if server == 'clear':
        if len(sys.argv) < 3:
            server = 'main'
        else:
            server = sys.argv[2]
        settings.removeConnection(server)
        sys.exit(0)

    connectionSettings = settings.getConnection(server)

    if not connectionSettings:
        if server == 'main' or server == 'ptr':
            legacyConfig = settings.getLegacySettings()
            if legacyConfig:
                if input("Upgrade settings file to the new format? (y/n) ") == "y":
                    settings.addConnection('main', legacyConfig['screeps_username'], legacyConfig['screeps_password'])
                    config = settings.getSettings()
                    config['smooth_scroll'] = legacyConfig['smooth_scroll']
                    config['max_scroll'] = legacyConfig['max_scroll']
                    config['max_history'] = legacyConfig['max_history']
                    settings.saveSettings(config)
                    connectionSettings = settings.getConnection(server)

    if not connectionSettings:
        if server is 'main':
            host = 'screeps.com'
            secure = True
        else:
            host = input("Host: ")
            secure = input("Secure (y/n) ") == "y"
        username = input("Username: ")
        password = input("Password: ")
        settings.addConnection(server, username, password, host, secure)

    if server == 'main' and 'token' not in connectionSettings:
        settings.addConnection('main', connectionSettings['username'], connectionSettings['password'])
        connectionSettings = settings.getConnection(server)

    ScreepsInteractiveConsole(server)
