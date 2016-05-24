# screeps_console

This project streams the Screeps console output to the terminal. It strips out
any html tags and adds colors.

![Screeps Interactive Console](docs/screenshot.png?raw=true "Screeps Interactive Console")


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
screeps_username:
screeps_password:
screeps_ptr: false
```


## Running

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


## Colors

Console output can have colors, in both the website version and teh shell. To get
the best of both worlds use font tags that also have a severity attribute.

```
<font color="#999999" severity="2">Message goes here!</font>
```

The severity can be anywhere from 0 to 5, with five beign the most extreme.
