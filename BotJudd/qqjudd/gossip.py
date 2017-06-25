import datetime
import json
import random
import re
from .bases import BaseAction
from .utils import loadfile, strip, savefile


def _gossip_list_append(gossip_list, pattern_raw, results):
    for each in gossip_list:
        if each[0].pattern == pattern_raw:
            each[1].extend(results)
            return
    pattern = re.compile(pattern_raw, flags=re.IGNORECASE)
    gossip_list.append((pattern, results))


def _get_gossip_list():
    gossip_list = []
    gossip_list_raw = loadfile('../data/gossip_list.txt').split('\n')[:-1]
    i = 0
    l = len(gossip_list_raw)
    while i < l:
        pattern_raw = gossip_list_raw[i]
        result_list = []
        i += 1
        while i < l and not gossip_list_raw[i].startswith('^'):
            result_list.append(gossip_list_raw[i])
            i += 1
        _gossip_list_append(gossip_list, pattern_raw, result_list)
    return gossip_list


def _check_gossip(content, **kwargs):
    content = strip(content)
    for each in reversed(Gossip.gossip_list):
        t = each[0].search(content)
        if t:
            return each
    return None


def _gossip():
    def update_message(self):
        tosub = random.sample(self.args[1], 1)[0]
        self.message = self.args[0].sub(tosub, self.content)
    return update_message


def _check_add_gossip(content, **kwargs):
    print(content)
    raw = None
    if content.startswith('/add_gossip '):
        raw = content[12:].strip()
    elif content.startswith('教你说话'):
        raw = content[4:].strip()
    else:
        return None

    i1 = raw.find('^')
    i2 = raw.find('$')
    if i1 < 0 or i2 < 0 or i2 == len(raw) - 1:
        return None
    return raw[i1:i2+1], raw[i2+1:].strip()


def _add_gossip():
    def update_message(self):
        try:
            _gossip_list_append(Gossip.gossip_list, self.args[0], [self.args[1]])
            self.message = '学会了'
        except:
            self.message = '我学习失败了'
    return update_message
            

class Gossip(BaseAction):
    gossip_list = _get_gossip_list()
    command_list = BaseAction.make_commands([
        [_check_gossip, 'gossip', _gossip()],
        [_check_add_gossip, 'addgossip', _add_gossip()],
    ])

    @staticmethod
    def update_gossip_list():
        Gossip.gossip_list = _get_gossip_list()


    def __init__(self, command, bot, contact, member, content, lang, args):
        super().__init__(command, bot, contact, member, content, lang, args)
        self.message = '我不知道该说什么'

    def handle(self):
        t = super().handle()
        self.sendMessage(self.message)
        return t

    @staticmethod
    def save_gossip_list():
        filename = '../log/%d.txt' % datetime.datetime.now().timestamp()
        glist = []
        for each in Gossip.gossip_list:
            glist.append(each[0].pattern)
            glist.extend(each[1])
        savefile(filename, '\n'.join(glist))

