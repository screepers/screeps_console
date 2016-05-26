#!/usr/bin/env python

import command
import json
import os
import outputparser
from settings import getSettings
import subprocess
import sys
from themes import themes
import urwid


class ScreepsInteractiveConsole:

    consoleWidget = False
    listWalker = False
    userInput = False

    def __init__(self):

        frame = self.getFrame()
        comp = self.getCommandProcessor()
        self.loop = urwid.MainLoop(urwid.AttrMap(frame, 'bg'), unhandled_input=comp.onInput, palette=themes['dark'])
        comp.setDisplayWidgets(self.loop, frame, self.getConsole(), self.getConsoleListWalker(), self.getEdit())
        console_monitor = ScreepsConsoleMonitor(self.consoleWidget, self.listWalker, self.loop)
        self.loop.run()


    def getFrame(self):
        urwid.AttrMap(self.getEdit(), 'input')
        frame_widget = urwid.Frame(
            header=self.getHeader(),
            body=self.getConsole(),
            footer=urwid.AttrMap(self.getEdit(), 'input'),
            focus_part='footer')
        return frame_widget



    def getHeader(self):
        return urwid.AttrMap(urwid.Text("Screeps Interactive Console", align='center'), 'header')

    def getEdit(self):
        if not self.userInput:
            self.userInput = urwid.Edit("> ")
        return self.userInput

    def getConsole(self):
        if not self.consoleWidget:
            self.consoleWidget = urwid.ListBox(self.getConsoleListWalker())
        return self.consoleWidget

    def getConsoleListWalker(self):
        if not self.listWalker:
            self.listWalker = urwid.SimpleListWalker([self.getWelcomeMessage()])
        return self.listWalker

    def getCommandProcessor(self):
        return command.Processor()

    def getWelcomeMessage(self):
        return urwid.Text(('default', 'Welcome to the Screeps Interactive Console'))


class ScreepsConsoleMonitor:

    proc = False

    def __init__(self, widget, walker, loop):
        self.widget = widget
        self.walker = walker
        self.loop = loop
        self.getProcess()

    def getProcess(self):
        if self.proc:
            return self.proc
        console_path = os.path.join(os.path.dirname(sys.argv[0]), 'console.py ')
        write_fd = self.loop.watch_pipe(self.onUpdate)
        self.proc = subprocess.Popen(
            [console_path + ' json'],
            stdout=write_fd,
            close_fds=True,
            shell=True)
        return self.proc

    def onUpdate(self, data):

        # If we lose the connection to the remote system close the console.
        if data.startswith('### closed ###'):
            self.proc = False
            self.getProcess()
            lostprocess_message = 'reconnecting to server . . .'
            self.walker.append(urwid.Text(('logged_response', lostprocess_message)))
            self.widget.set_focus(len(self.walker)-1)
            return

        data_lines = data.rstrip().split('\n')
        for line_json in data_lines:
            try:
                line = json.loads(line_json.strip())
                log_type = outputparser.getType(line)

                if log_type == 'result':
                    formatting = 'logged_response'
                elif log_type == 'highlight':
                    formatting = 'highlight'
                elif log_type == 'error':
                    formatting = 'error'
                else:
                    severity = outputparser.getSeverity(line)
                    if not severity or severity > 5 or severity < 0:
                        formatting = 'highlight'
                    else:
                        formatting = 'severity' + str(severity)

                line = line.replace('&#09;', " ")
                line = outputparser.clearTags(line)
                self.walker.append(urwid.Text((formatting, line)))
                if len(self.walker) > 0:
                    self.widget.set_focus(len(self.walker)-1)
            except:
                ''

    def __del__(self):
        self.proc.kill()


if __name__ == "__main__":
    ScreepsInteractiveConsole()
