import datetime
import json
import random
import requests
from .utils import jsonload

_cache = {'schedule': None}

_stages = jsonload('data/stages.json')
_modes = jsonload('data/modes.json')
_ranked_modes = _modes.copy()
_ranked_modes.pop('Turf War')

def _cached_stages(now):
    for each in _cache['schedule']:
        if each['startTime'] <= now < each['endTime']:
            return each
    return None

def _update_cache():
    tmp = requests.get('http://glsplatoon.com/SVN/json').json()
    _cache['schedule'] = tmp['schedule']


def _get_sometime_stages(sometime, force=False):
    t = sometime.timestamp() * 1000
    if force or not _cache['schedule'] or _cache['schedule'][-1]['endTime'] <= t:
        _update_cache()
    return _cached_stages(t)


def _get_name(stage, lang, alias):
    if alias:
        names = stage['alias']
        if names:
            return random.sample(names, 1)[0]
    return stage.get(lang)


def get_cached_stages(force=False, lang='zh', alias=False):
    if force or not _cache['schedule']:
        _update_cache()
    ret = []
    for each in _cache['schedule']:
        ret.append({
            'startTime': datetime.datetime.fromtimestamp(each['startTime'] / 1000),
            'endTime': datetime.datetime.fromtimestamp(each['endTime'] / 1000),
            'stages': [{'maps': tuple(_get_name(_stages[x['nameEN']], lang, alias) for x in each['regular']['maps']),
            'mode': _modes[each['regular']['rules']['en']].get(lang)},
            {'maps': tuple(_get_name(_stages[x['nameEN']], lang, alias) for x in each['ranked']['maps']),
            'mode': _modes[each['ranked']['rules']['en']].get(lang)}]
        })
    return ret


def get_current_turf_stages(force=False, lang='zh', alias=False):
    stages = _get_sometime_stages(datetime.datetime.now(), force)
    maps = tuple(_get_name(_stages[x['nameEN']], lang, alias) for x in stages['regular']['maps'])
    mode = _modes[stages['regular']['rules']['en']].get(lang)
    return {'maps': maps, 'mode': mode}


def get_current_ranked_stages(force=False, lang='zh', alias=False):
    stages = _get_sometime_stages(datetime.datetime.now(), force)
    maps = tuple(_get_name(_stages[x['nameEN']], lang, alias) for x in stages['ranked']['maps'])
    mode = _modes[stages['ranked']['rules']['en']].get(lang)
    return {'maps': maps, 'mode': mode}


def get_current_stages(force=False, lang='zh', alias=False):
    return [get_current_turf_stages(force, lang, alias),
            get_current_ranked_stages(force, lang, alias)]


def get_sometime_stages(sometime, force=False, lang='zh', alias=False):
    stages = _get_sometime_stages(sometime, force)
    if stages is None:
        return None
    return [{'maps': tuple(_get_name(_stages[x['nameEN']], lang, alias) for x in stages[mode]['maps']),
    'mode': _modes[stages[mode]['rules']['en']].get(lang)} for mode in ['regular', 'ranked']]


def get_random_stages(ranked=True, number=1, lang='zh', alias=False):
    ret = []
    for i in range(number):
        while True:
            stage = _get_name(_stages[random.sample(_stages.keys(), 1)[0]], lang, alias)
            mode = _modes[random.sample(_ranked_modes.keys() if ranked else _modes.keys(), 1)[0]].get(lang)
            p = {'map': stage, 'mode': mode}
            if p in ret:
                continue
            ret.append(p)
            break
    return ret

