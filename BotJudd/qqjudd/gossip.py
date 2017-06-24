import random
import re
from .bases import BaseAction

class Gossip(BaseAction):
    def __init__(self, command, bot, contact, member, lang, **kwargs):
        super().__init__(bot, contact, member, lang)
        self.command = command
        self.args = kwargs.get('args')

    def handle(self):
        self.message = '我不知道该说什么'
        if self.command == 'laxi':
            target = self.args[0]
            self.message = '拉稀%s！' % target
        elif self.command == 'wow':
            self.message = '喵' * random.randint(1, 5)
        elif self.command == 'who':
            self.message = '我是猫裁判！'
        elif self.command == 'catfilm':
            self.message = '不存在的。'
        self.sendMessage(self.message)
        return None

    @classmethod
    def check_handle(cls, bot, contact, member, content, lang):
        if content == '哇':
            return cls('wow', bot, contact, member, lang)
        if content == '你是谁':
            return cls('who', bot, contact, member, lang)
        if content == '求猫片' or content == '我要看猫片':
            return cls('catfilm', bot, contact, member, lang)
        q = re.match(r'^拉稀(.*)$', content)
        if q:
            args = (q.groups()[0],)
            return cls('laxi', bot, contact, member, lang, args=(q.groups()[0],))
        return None
