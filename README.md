# screeps_console

This project streams the Screeps console output to the terminal. It strips out
any html tags and adds colors.

![Screeps Interactive Console](docs/screenshot.png?raw=true "Screeps Interactive Console")


## Requirements

* python
* ncurses (typically already on most \*nix systems)
* pip
* cygwin (if on Windows)


## Installation

Note: This application runs on both Python 2 and Python 3.

1. Make sure you have `pip` installed. On Mac OS X do `sudo easy_install pip`
1. Make sure `virtualenv` is installed- `pip install virtualenv`
1. Clone this GitHub repo and go into the cloned directory
1. Determine where your Python is installed with `which python` - assume it is `/path/to/python` and replace that below
1. Set up the `virtualenv` with the command `virtualenv -p /path/to/python env`
1. Use that new `virtualenv` with the command `source env/bin/activate`
1. Run `make`
1. Run `make install`
1. Run `screepsconsole` from inside the terminal


## Settings

The settings file is created automatically and placed in `~.screepsconsole.yaml`.

Typically there is little reason to edit it manually. When you attempt to connect
to a server for the first time it will ask for your credentials (and if it's a
private server for the host), which will then be saved for future use.

When using the "screeps.com" server the console will automatically create a
token and use that instead of storing your credentials.

## Launching

The interactive shell can be used for both reading console output and sending
console commands to the server.

```bash
$ screepsconsole
```

By default it connects to the main server, but it can also connect to PTR.

```bash
$ screepsconsole ptr
```

The system also works with private servers. Any label can be used, and unlike
the main server the system will ask for a host (include the port) and whether
the shard uses https.

```bash
$ screepsconsole screepsplus
```

It is possible to clear a saved connection.

```bash
$ screepsconsole clear connectionname
```

You can also call the python script directly.

```bash
$ ./screeps_console/interactive.py
```


## Streaming Console

To stream the console output directly to your terminal's stdout without the
ability to send command use the `console.py` application.

```bash
$ ./screeps_console/console.py
```

Like the Interactive version different servers can be specified.

```bash
$ ./screeps_console/console.py ptr
```

The output can also be sent in JSON.

```bash
$ ./screeps_console/console.py main json
```


## Interactivity

The interactive console allows you to directly interact with your screeps
program through the in game console. Most of the time what you put in will be
sent directly to the screeps server to be processed. There are a few built in
commands however.

* `about` - displays information about the program.
* `clear` - resets the console display.
* `console` - allows users to suppress normal console output and only sure user interactions.
* `disconnect` - disconnects the console from the Screeps server.
* `exit` - exits the shell.
* `filter` - applies filters to the console output.
* `list` - lists these and other built in commands and aliases.
* `pause` - disables autoscrolling (hit enter on an empty terminal to reenable).
* `reconnect` - reconnects the console to the Screeps server.
* `shard` - controls the active shards.
* `themes` - lists available themes when called without an argument, or switches.
  Otherwise switches themes when called with the theme name as the first
  argument.
* `time` - displays the time (in ticks) on the Screeps server.


## Scrolling

Scrolling can be done one line at a time using `alt up` and `alt down`. Using
`PageUp` and `PageDown` (FN+up and FN+down on Apple) can be used to scroll
through the console buffer a bit quicker.

## Shards

By default all output from all shards is displayed and console commands go to
shard0. This can be changed with the `shard` commands.

* `shard` - by itself it outputs the shard that console input will go to.
* `shard SHARDNAME` - changes the shard that console input goes to.
* `shard focus SHARDNAME` - changes the console output and only displays
  messages from this shard.
* `shard clear` - display all output from all shards, but leave the console
  input pointed at the same shard.


## Filters

Console output can be filtered using regular expressions and the `filter`
command. Only commands that match at least one filter will be displayed.

* `filter list` - this lists each current regex filter and its index.
* `filter add REGEX` - add a regular expression to the filter list.
* `filter clear` - remove all filters.
* `filter contains STRING` - add a filter that looks for log lines that contain
  the supplied string.
* `filter remove INDEX` - remove a regular expression using it's index.


## Colors and Severity

Console output can have colors, in both the website version and the shell. To
get the best of both worlds use font tags that also have a severity attribute.

```
<font color="#999999" severity="2">Message goes here!</font>
```

The severity can be anywhere from 0 to 5, with five being the most extreme. In
addition you can highlight a log line by giving it the 'type' of 'highlight'.

```
<font color="#ffff00" type="highlight">This message will stand out!</font>
```

If you do not care about coloring the web console output you can use a simpler
format.

```
<log severity="2">Message goes here</log>
<log type="highlight">This message will stand out!</log>
```

An [example logger](docs/ExampleLogger.js) is included in the docs folder to
demonstrate how this works.
