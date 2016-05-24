#!/usr/bin/env python

import colorama
import json
import os
from outputparser import getSeverity
from outputparser import clearTags
from outputparser import getType
from screeps import ScreepsConnection
from settings import getSettings
import subprocess
import sys
import urwid


class ScreepsInteractiveConsole:

    consoleWidget = False
    listWalker = False
    userInput = False
    apiclient = False

    palette = [
        ('header', 'bold, white', 'dark gray'),
        ('input', 'white', 'dark blue'),
        ('logged_input', 'dark magenta', 'black'),
        ('logged_response', 'light magenta', 'black'),
        ('error', 'yellow', 'dark red'),

        ('severity0', 'light gray', 'black'),
        ('severity1', 'dark blue', 'black'),
        ('severity2', 'dark cyan', 'black'),
        ('severity3', 'dark green', 'black'),
        ('severity4', 'light red', 'black'),
        ('severity5', 'yellow', 'dark red'),
        ('highlight', 'black', 'yellow'),
    ]


    def __init__(self):

        self.loop = urwid.MainLoop(self.getFrame(), unhandled_input=self.catch_user_input, palette=self.palette)
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
            welcome = self.getWelcomeMessage()
            self.consoleWidget = urwid.ListBox(self.getConsoleListWalker())
        return self.consoleWidget

    def getConsoleListWalker(self):
        if not self.listWalker:
            self.listWalker = urwid.SimpleFocusListWalker([self.getWelcomeMessage()])
        return self.listWalker


    def catch_user_input(self, key):

        if key == 'enter':
            userInput = self.getEdit()
            user_text = userInput.get_edit_text()
            userInput.set_edit_text('')

            walker = self.getConsoleListWalker()
            walker.append(urwid.Text(('logged_input', '> ' + user_text)))

            if len(walker) > 0:
                self.getConsole().set_focus(len(walker)-1)

            if user_text == 'exit':
                raise urwid.ExitMainLoop()

            if len(user_text) > 0:
                apiclient = self.getApiClient()
                result = apiclient.console(user_text)

        return

    def getWelcomeMessage(self):
        return urwid.Text(('welcome_message', 'Welcome to the Screeps Interactive Console'))


    def getApiClient(self):
        if not self.apiclient:
            settings = getSettings()
            self.apiclient = ScreepsConnection(u=settings['screeps_username'],p=settings['screeps_password'],ptr=settings['screeps_ptr'])
        return self.apiclient



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
        data_lines = data.rstrip().split('\n')
        for line_json in data_lines:
            try:
                line = json.loads(line_json.strip())
                log_type = getType(line)

                if log_type == 'result':
                    formatting = 'logged_response'
                elif log_type == 'highlight':
                    formatting = 'highlight'
                elif log_type == 'error':
                    formatting = 'error'
                else:
                    severity = getSeverity(line)
                    if not severity or severity > 5 or severity < 0:
                        formatting = 'highlight'
                    else:
                        formatting = 'severity' + str(severity)

                line = line.replace('&#09;', " ")
                line = clearTags(line)
                self.walker.append(urwid.Text((formatting, line)))
                if len(self.walker) > 0:
                    self.widget.set_focus(len(self.walker)-1)
            except:
                ''

    def __del__(self):
        self.proc.kill()


if __name__ == "__main__":
    ScreepsInteractiveConsole()
