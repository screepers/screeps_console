
from autocomplete import Autocomplete
import calendar
from screeps import ScreepsConnection
from settings import getSettings
import re
from themes import themes
import time
import urwid


class Processor(object):
    lastkey = False
    apiclient = False
    aliases = {
        'theme': 'themes',
        'time': 'Game.time',
        'help': 'list'
    }

    def __init__(self):
        self.lastkeytime = 0
        self.listbox = False
        self.listwalker = False
        self.consolemonitor = False
        self.edit = False
        self.getApiClient()
        self.autocomplete = Autocomplete(self)

    def setDisplayWidgets(self, loop, frame, listbox, listwalker, edit, consolemonitor):
        self.listbox = listbox # console
        self.listwalker = listwalker
        self.edit = edit
        self.loop = loop
        self.consolemonitor = consolemonitor

    def getApiClient(self):
        if not self.apiclient:
            settings = getSettings()
            self.apiclient = ScreepsConnection(
                           u=settings['screeps_username'],
                           p=settings['screeps_password'],
                           ptr=settings['screeps_ptr'])
        return self.apiclient

    def onInput(self, key):

        lastkeytime = self.lastkeytime
        self.lastkeytime = calendar.timegm(time.gmtime())

        if self.lastkeytime - lastkeytime > 1:
            self.lastkey = False

        lastkey = self.lastkey
        self.lastkey = key

        if not self.listbox:
            return

        if key == 'enter':
            self.onEnter(key)
            return

        if key == 'tab' and lastkey == 'tab':
            self.onTab(key)
            return

        if key == 'page up':
            self.onPageUp(key)
            return

        if key == 'page down':
            self.onPageDown(key)
            return

        if key == 'meta up':
            self.onMetaUp(key)
            return

        if key == 'meta down':
            self.onMetaDown(key)
            return


        return

    def onEnter(self, key):
        self.listbox.setAutoscroll(True)
        userInput = self.edit
        user_text = userInput.get_edit_text()

        # Check for builtin commands before passing to the screeps api.
        user_command_split = user_text.split(' ')
        first_command = user_command_split[0]

        # Check to see if command is actually an alias
        if first_command in self.aliases:
            first_command = self.aliases[first_command]
            user_command_split[0] = first_command
            user_text = ' '.join(user_command_split)

        # Look for built in commands before attempting API call.
        builtin = Builtin()
        if hasattr(builtin, first_command):
            self.listwalker.append(
                urwid.Text(('logged_input', '> ' + user_text)))
            builtin_command = getattr(builtin, first_command)
            builtin_command(self)
            self.listbox.autoscroll()
            userInput.set_edit_text('')
            return

        # Send command to Screeps API. Output will come from the console stream.
        if len(user_text) > 0:
            self.listwalker.append(
                urwid.Text(('logged_input', '> ' + user_text)))
            self.listbox.scrollBottom()
            userInput.set_edit_text('')
            apiclient = self.getApiClient()
            apiclient.console(user_text)

    def onTab(self, key):
        self.autocomplete.complete()
        pass

    def onPageUp(self, key):
        info = self.loop.screen.get_cols_rows()
        self.listbox.scrollUp(int(info[1] / 3))

    def onPageDown(self, key):
        info = self.loop.screen.get_cols_rows()
        self.listbox.scrollDown(int(info[1] / 3))

    def onMetaUp(self, key):
        self.listbox.scrollUp(1)

    def onMetaDown(self, key):
        self.listbox.scrollDown(1)



class Builtin(object):

    def about(self, comp):
        about = 'Screeps Interactive Console by Robert Hafner <tedivm@tedivm.com>'  # noqa
        comp.listwalker.append(urwid.Text(('logged_response', about)))
        about = 'https://github.com/screepers/screeps_console'
        comp.listwalker.append(urwid.Text(('logged_response', about)))
        return


    def buffer(self, comp):
        comp.listwalker.append(urwid.Text(('logged_response', str(len(comp.listwalker)))))
        return


    def clear(self, comp):
        comp.listbox.set_focus_pending = 0
        comp.listwalker[:] = [urwid.Text('')]
        return

    def exit(self, comp):
        raise urwid.ExitMainLoop()

    def filter(self, comp):

        user_text = comp.edit.get_edit_text()
        user_command_split = user_text.split(' ')

        if len(user_command_split) <= 1:
            subcommand = 'list'
        else:
            subcommand = user_command_split[1]

        if subcommand == 'list':
            filters = comp.consolemonitor.filters[:]

            if len(filters) <= 0:
                comp.listwalker.append(urwid.Text(('logged_response', 'No filters')))
                comp.listbox.autoscroll()
                return
            else:
                for index, pattern in enumerate(filters):
                    comp.listwalker.append(urwid.Text(('logged_response', str(index) + '. ' + pattern)))
                    comp.listbox.autoscroll()
                return

        elif subcommand == 'add':
            regex = user_command_split[2:]
            comp.consolemonitor.filters.append(' '.join(regex))

        elif subcommand == 'clear':
            comp.consolemonitor.filters = []

        elif subcommand == 'contains':
            remaining_commands = user_command_split[2:]
            matchstring = ' '.join(remaining_commands)
            matchstring_escaped = '.*' + re.escape(matchstring) + '.*'
            comp.consolemonitor.filters.append(matchstring_escaped)

        elif subcommand == 'remove':
            toRemove = user_command_split[2]
            comp.consolemonitor.filters.pop(int(toRemove))



    def list(self, comp):
        command_list = ''
        aliases = list(comp.aliases)
        builtin_list = [method for method in dir(self) if callable(getattr(self, method))]
        commands = builtin_list

        for alias in aliases:
            alias_real = comp.aliases[alias]
            if alias_real not in builtin_list:
                commands.append(alias)

        commands.sort()
        commands.reverse()
        for builtin_command in commands:
            if builtin_command != 'turtle' and not builtin_command.startswith('__'):
                command_list = builtin_command + '  ' + command_list

        comp.listwalker.append(urwid.Text(('logged_response', command_list)))
        return

    def pause(self, comp):
        comp.listbox.setAutoscroll(False)

    def themes(self, comp):
        userInput = comp.edit
        user_text = userInput.get_edit_text()
        user_command_split = user_text.split(' ')
        if len(user_command_split) < 2 or user_command_split[1] == 'list':
            theme_names = themes.keys()
            theme_names.reverse()
            theme_list = ''
            for theme in theme_names:
                theme_list = theme + '  ' + theme_list

            comp.listwalker.append(urwid.Text(('logged_response', theme_list)))
            return

        if user_command_split[1] == 'test':
            comp.listwalker.append(urwid.Text(('logged_input', 'logged_input')))
            comp.listwalker.append(urwid.Text(('logged_response', 'logged_response')))
            comp.listwalker.append(urwid.Text(('error', 'error')))
            comp.listwalker.append(urwid.Text(('default', 'default')))
            comp.listwalker.append(urwid.Text(('severity0', 'severity0')))
            comp.listwalker.append(urwid.Text(('severity1', 'severity1')))
            comp.listwalker.append(urwid.Text(('severity2', 'severity2')))
            comp.listwalker.append(urwid.Text(('severity3', 'severity3')))
            comp.listwalker.append(urwid.Text(('severity4', 'severity4')))
            comp.listwalker.append(urwid.Text(('severity5', 'severity5')))
            comp.listwalker.append(urwid.Text(('highlight', 'highlight')))
            comp.listbox.set_focus(len(comp.listwalker)-1)
            return

        theme = user_command_split[1]
        if theme in themes:
            comp.loop.screen.register_palette(themes[theme])
            comp.loop.screen.clear()

        return

    def turtle(self, comp):
        turtle = '''
 ________________
< How you doing? >
 ----------------
    \                                  ___-------___
     \                             _-~~             ~~-_
      \                         _-~                    /~-_
             /^\__/^\         /~  \                   /    \\
           /|  O|| O|        /      \_______________/        \\
          | |___||__|      /       /                \          \\
          |          \    /      /                    \          \\
          |   (_______) /______/                        \_________ \\
          |         / /         \                      /            \\
           \         \^\\\         \                  /               \     /
             \         ||           \______________/      _-_       //\__//
               \       ||------_-~~-_ ------------- \ --/~   ~\    || __/
                 ~-----||====/~     |==================|       |/~~~~~
                  (_(__/  ./     /                    \_\      \.
                         (_(___/                         \_____)_)
'''
        comp.listwalker.append(urwid.Text(('logged_response', turtle)))
        comp.listwalker.append(urwid.Text(('logged_response', '')))
