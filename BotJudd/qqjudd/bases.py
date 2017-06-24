from .utils import strip

class BaseAction():
    _LANGS = {'en', 'zh', 'jp'}

    def __init__(self, bot, contact, member, lang):
        self.bot = bot 
        self.contact = contact
        self.member = member
        self.lang = lang

    @classmethod
    def check_handle(cls, bot, contact, member, content):
        if member is None or member.uin == bot.conf.qq:
            return None, None
        p = content.find(' ')
        if p < 0:
            return None, None
        if content[:p].strip() != '[@ME]':
            return None, None
        content = content[p + 1:].strip()
        p = content.find(' ')
        lang = 'zh'
        if p >= 0 and content[:p] in BaseAction._LANGS:
            lang = content[:p]
            content = strip(content[p + 1:])
        return content, lang
    
    def sendMessage(self, message):
        t = '@' + self.member.name + '\n'
        self.bot.SendTo(self.contact, t + message)
