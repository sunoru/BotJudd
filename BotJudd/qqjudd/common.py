import math
import random
import re
from .bases import BaseAction
from .utils import parse_number


def _random_int():
    def update_message(self):
        n = self.args.get('n')
        if not n:
            n = 1
        m = self.args.get('m')
        if not m:
            m = 6
        n, m = map(parse_number, (n, m))
        if not n or not m or n < 0 or m < 0 or n * math.log10(m) > 100:
            self.messages = ['喵喵喵？']
            return
        numbers = [str(random.randint(1, m)) for i in range(n)]
        self.messages = ['得到的数字为：', ', '.join(numbers)]
    return update_message


class CommonAction(BaseAction):
    command_list = BaseAction.make_commands([
        [r'^投(?P<n>.*?)个((?P<m>.*?)面)?的?[骰色]子', 'randomint', _random_int()]
    ])

    def __init__(self, command, bot, contact, member, content, lang, args):
        super().__init__(command, bot, contact, member, content, lang, args)
        self.messages = None

    def handle(self):
        t = super().handle()
        if self.messages:
            self.sendMessage('\n'.join(self.messages))
        if callable(t):
            self.handle_next = t
            return self
        return t
