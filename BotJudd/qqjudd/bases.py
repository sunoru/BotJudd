from collections import namedtuple
import re
from .utils import strip, settings

Command = namedtuple('Command', ['check', 'name', 'handle', 'args'])


class BaseAction():
    _LANGS = {'en', 'zh', 'jp'}

    def __init__(self, command, bot, contact, member, content, lang, args):
        self.command = command
        self.bot = bot 
        self.contact = contact
        self.member = member
        self.content = content
        self.lang = lang
        self.args = args

    @classmethod
    def check_handle_message(cls, bot, contact, member, content):
        if contact.qq not in settings.ALLOWED_GROUPS or member is None or member.uin == bot.conf.qq:
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
            content = content[p + 1:].strip()
        return content, lang

    @classmethod
    def check_handle(cls, bot, contact, member, content, lang):
        for command in cls.command_list:
            check_ret = command.check(bot=bot, contact=contact, member=member, content=content, lang=lang)
            if check_ret is not None:
                return cls(command, bot, contact, member, content, lang, check_ret)
        return None

    def handle(self):
        return self.command.handle(self, *self.command.args)

    @staticmethod
    def make_command(arg_list):
        pattern = arg_list[0]
        if len(arg_list) < 3:
            return None
        if isinstance(pattern, str):
            pattern = re.compile(pattern, flags=re.IGNORECASE)
            def matching_func(content, **kwargs):
                content = strip(content)
                x = pattern.match(content)
                if not x:
                    return None
                return x.groupdict()
        elif callable(pattern):
            matching_func = pattern
        else:
            return None
        return Command(matching_func, arg_list[1], arg_list[2], arg_list[3:])

    @staticmethod
    def make_commands(commands):
        return list(map(BaseAction.make_command, commands))
    
    def sendMessage(self, message):
        t = '@' + self.member.name
        if '\n' in message or len(message) > 12:
            t += '\n'
        else:
            t += ' '
        self.bot.SendTo(self.contact, t + message)

