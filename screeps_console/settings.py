from collections import OrderedDict
import json
import os
from os.path import expanduser
import yaml
import screepsapi
import requests


userhome = expanduser('~')
settingsfile = userhome + '/.screepsconsole.yaml'


def getSettings():
    if not os.path.isfile(settingsfile):
        settings = {
            'connections': {},
            'max_history': 200000,
            'max_scroll': 200000,
            'smooth_scroll': True
        }
        saveSettings(settings)
        return settings
    with open(settingsfile, 'r') as f:
        settings = yaml.safe_load(f)
    return settings


def getConnection(name):
    settings = getSettings()

    if not settings:
        return False

    if 'connections' not in settings:
        return False

    if name not in settings['connections']:
        return False

    return settings['connections'][name]


def addConnection(name, username, password, host=False, secure=False):
    if name == 'main':
        secure = True
        host = 'screeps.com'
        #addConnection('ptr', username, password)
    if name == 'ptr':
        secure = True
        host = 'screeps.com/ptr'

    settings = getSettings()
    if not settings:
        settings = {}

    if 'connections' not in settings:
        settings['connections'] = {}

    if name == 'main' or name == 'ptr':
        token = getToken(username, password, host, secure)
        settings['connections'][name] = {
            'host': host,
            'secure': secure,
            'token': token
        }
    else:
        settings['connections'][name] = {
            'host': host,
            'secure': secure,
            'username': username,
            'password': password
        }

    saveSettings(settings)


def getToken(username, password, host, secure):
    if secure:
        apiurl = 'https://%s/api/user/auth-token' % (host)
    else:
        apiurl = 'http://%s/api/user/auth-token' % (host)

    authtype = {"type": "full",
                "endpoints": {
                    "GET /api/user/name": False,
                    "GET /api/user/money-history": False,
                    "GET /api/market/my-orders": False,
                    "GET /api/user/memory": False,
                    "GET /api/user/memory-segment": False,
                    "POST /api/user/memory-segment": False},
                "websockets": {
                    "console": False,
                    "rooms": False},
                "memorySegments": ""
               }
    r = requests.post(apiurl, data=authtype, auth=(username, password))
    r.raise_for_status()
    apiret = json.loads(r.text, object_pairs_hook=OrderedDict)
    return apiret['token']


def removeConnection(name):
    if name == 'main':
        removeConnection('ptr')
    if not getConnection(name):
        return False
    config = getSettings()
    del config['connections'][name]
    saveSettings(config)


def saveSettings(settings):
    with open(settingsfile, 'w') as outfile:
        yaml.dump(settings, outfile, default_flow_style=False)


def getApiClient(name):
    settings = getConnection(name)
    if 'token' in settings:
        return screepsapi.API(
            token=settings['token'],
            host=settings['host'],
            secure=settings['secure'],
        )
    else:
        return screepsapi.API(
            u=settings['username'],
            p=settings['password'],
            host=settings['host'],
            secure=settings['secure'],
        )







def getLegacySettings():
    if not getLegacySettings.settings:
        cwd = os.getcwd()
        path = cwd + '/.settings.yaml'

        if not os.path.isfile(path):
            path = cwd + '/.screeps_settings.yaml'

        if not os.path.isfile(path):
            path = expanduser('~') + '/.screeps_settings.yaml'

        if not os.path.isfile(path):
            return False

        with open(path, 'r') as f:
            getLegacySettings.settings = yaml.load(f)

    return getLegacySettings.settings

getLegacySettings.settings = False
