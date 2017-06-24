import re
from BotJudd import splatoon
from .bases import BaseAction
from .utils import parse_number, strip

class WeaponInfo(BaseAction):
    help_info = '''
        武器相关：
        随机三把武器[,带Amiibo,不带剧情武器]
    '''
    # TODO: 小绿是什么
    def __init__(self, command, bot, contact, member, lang, **kwargs):
        super().__init__(bot, contact, member, lang)
        self.command = command
        if command == 'randomweapons':
            n, amiibo, scroll = kwargs['args']
            if n > 12:
                self.messages = ['最多生成 12 把武器']
            else:
                self.messages = splatoon.get_random_weapons(scroll, amiibo, n, lang)

    def handle(self):
        self.sendMessage('\n'.join(self.messages))
        return None

    @staticmethod
    def check_handle_random(content):
        amiibo = False
        scroll = True
        if content.startswith('/randomweapons'):
            try:
                p = strip(content[14:])
                if not p:
                    return 1, amiibo, scroll
                p = p.split()
                for i in range(1, len(p)):
                    if p[i] == 'amiibo':
                        amiibo = True
                    elif p[i] == 'noscroll':
                        scroll = False
                return int(p[0]), amiibo, scroll
            except ValueError:
                return None
        content = strip(content)
        if re.search(r'带\s*Amiibo', content, flags=re.IGNORECASE):
            amiibo = True
            content = re.sub(r'带\s*Amiibo', '', content, flags=re.IGNORECASE)
            content = strip(content)
        if content.find('不带剧情武器') >= 0:
            scroll = False
            content = strip(content.replace('不带剧情武器', ''))

        q = re.match(r'^随机(.*)把武器$', content)
        if not q:
            q = re.match(r'^随机武器(.+)把$', content)
        if q:
            p = q.groups()[0]
            if not p:
                return 1, amiibo, scroll
            t = parse_number(p)
            if t is None:
                return 2007012811, amiibo, scroll
            return t, amiibo, scroll
        return None


    @classmethod
    def check_handle(cls, bot, contact, member, content, lang):
        t = WeaponInfo.check_handle_random(content)
        if t is not None:
            return cls('randomweapons', bot, contact, member, lang, args=t)
        return None
