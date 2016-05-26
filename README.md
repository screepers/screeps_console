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

1. Download this package, either from the Releases page or from a git clone.

2. Install dependencies using `pip`. While not required, it's recommended that
   you use [virtualenv](http://www.bogotobogo.com/python/python_virtualenv_virtualenvwrapper.php)
   rather than installing your repositories globally.

```
pip install -r requirements.txt
```

## Settings

The settings file is a yaml file. Begin by copying the settings.dist file to
.settings.yaml in the directory you will be calling `notify.py` from.

```
cp .settings.dist.yaml .settings.yaml
```

The settings file is in yaml and takes various authentication tokens.

```yaml
# Copy this to .settings.yaml and fill it out.

# Screeps account info
# Your username is your full email address.
screeps_username:
screeps_password:
screeps_ptr: false

# Proxy configuration
http_proxy:
http_proxy_port:
```


## Launching

To stream the console output directly to your terminal's stdout run the
`console.py` application.

```bash
$ ./screeps_console/console.py
```


This project also offers an interactive shell that can be used for both reading
console output and sending console commands to the server.

```bash
$ ./screeps_console/interactive.py
```

## Interactivity

The interactive console allows you to directly interact with your screeps
program through the in game console. Most of the time what you put in will be
sent directly to the screeps server to be processed. There are a few built in
commands however.

* clear - resets the console display.
* exit - exits the shell.
* list - lists these and other built in commands and aliases.
* pause - disables autoscrolling (hit enter on an empty terminal to reenable).
* themes - lists available themes when called without an argument, or switches
  themes when called with the theme name as the first argument

## Scrolling

PageUP and PageDOWN (FN+up and FN+down on Apple) can be used to scroll through
the console buffer.


## Colors and Severity

Console output can have colors, in both the website version and the shell. To get
the best of both worlds use font tags that also have a severity attribute.

```
<font color="#999999" severity="2">Message goes here!</font>
```

The severity can be anywhere from 0 to 5, with five beign the most extreme.
