
import colorama
from colorama import Fore, Back, Style
import re

colorama.init()
SEVERITY_RE = re.compile(r'<.*severity="(\d)">')
TAG_RE = re.compile(r'<[^>]+>')

def parseLine(line):
    severity = getSeverity(line)

    # Add color based on severity
    if 'severity' not in locals():
        severity = 3

    if severity == 0:
        color = Style.DIM + Fore.WHITE
    elif severity == 1:
        color = Style.NORMAL + Fore.BLUE
    elif severity == 2:
        color = Style.NORMAL + Fore.CYAN
    elif severity == 3:
        color = Style.NORMAL + Fore.WHITE
    elif severity == 4:
        color = Style.NORMAL + Fore.RED
    elif severity == 5:
        color = Style.NORMAL + Fore.BLACK + Back.RED
    else:
        color = Style.NORMAL + Fore.BLACK + Back.YELLOW

    # Replace html tab entity with actual tabs
    line = clearTags(line)
    line = line.replace('&#09;', "\t")
    return color + line + Style.RESET_ALL


def tagLine(line):
    severity = str(getSeverity(line))
    line = clearTags(line)
    return '<log severity=' + severity + '>' + line + '</log>'


def clearTags(line):
    try:
        line = TAG_RE.sub('', line)
        return line
    except:
        return line


def getSeverity(line):
    if '<' in line:
        try:
            match_return = SEVERITY_RE.match(line)
            groups = match_return.groups()
            if len(groups) > 0:
                return int(groups[0])
            else:
                return false
        except:
            return false
    else:
        return 3
