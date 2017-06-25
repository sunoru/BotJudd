import datetime
import re
from .bases import BaseAction


def _ask_squad():
    def handle(self):
        self.people = [(self.member, datetime.datetime.now())]
        self.message = '现在没人排，把你记下来了'
        return self
    return handle

class SquadInfo(BaseAction):
    help_info = '''
        组排相关：
        有人排吗？
        我也要排
    '''
    command_list = BaseAction.make_commands([
        [r'^(/asksquad|((现在)|([待一]会儿?))?有(没有)?[谁人]?要?[组排]排*吗?|我?也?要?组?排+)$', 'asksquad', _ask_squad()]
    ])

    def __init__(self, command, bot, contact, member, content, lang, args):
        super().__init__(command, bot, contact, member, content, lang, args)
        self.people = []
        self.messages = None

    def handle(self):
        t = super().handle()
        if self.message:
            self.sendMessage(self.message)
        return t

    def find_member(self, member):
        if isinstance(member, str):
            cmp_f = lambda p: p[0].name == member
        else:
            cmp_f = lambda p: p[0].uin == member.uin
        for i, p in enumerate(self.people):
            if cmp_f(p):
                return i
        return -1

    def show_people(self):
        return '这些人在等待组排：\n' + '\n'.join(
            '%s %s' % (p[1].strftime('%H:%M'), p[0].name)
            for p in self.people
        )

    def handle_next(self, bot, contact, member, content, lang):
        if contact.uin != self.contact.uin:
            return None
        asked = self.find_member(member)
        alive = True
        if re.search(r'^(/showsquad|显示([求等]?[组排]排*|等待组排)列表)$', content):
            self.message = self.show_people()
        elif SquadInfo.command_list[0][0](content) is not None:
            if asked >= 0:
                self.message = ''
            else:
                self.message = '把你记下来了\n'
                self.people.append((member, datetime.datetime.now()))
            self.message += self.show_people()
        elif re.search(r'^(/cancelsquad|我?不求?[组排]排*了)$', content):
            if asked >= 0:
                self.people.pop(asked)
                self.message = '好，把你从等待组排列表里删去了'
                if not self.people:
                    alive = False
            else:
                self.message = '你本来也没说要排呀'
        elif re.search(r'^我和(.+?)去?[组排]排*了$', content):
            names_raw = re.match(r'^我和(?P<names>.+?)去?[组排]排*了$', content).groupdict()['names']
            names = filter(lambda x: x, names_raw.split('@'))
            indices = set(filter(lambda x: x >= 0, map(self.find_member, names)))
            if asked < 0 and len(indices) == 0:
                self.message = '哦'
            else:
                if asked >= 0:
                    indices.add(asked)
                indices = sorted(indices, reverse=True)
                for index in indices:
                    self.people.pop(index)
                print(self.people)
                self.message = '好，把你们从等待组排列表里删去了'
                if not self.people:
                    alive = False
        else:
            return None
        self.member = member
        self.sendMessage(self.message)
        return alive
