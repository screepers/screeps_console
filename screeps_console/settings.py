import os
import sys
import yaml


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
