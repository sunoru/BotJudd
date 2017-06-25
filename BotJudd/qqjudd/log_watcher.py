from .utils import settings

logs = {}

class LogWatcher():
    @staticmethod
    def process(bot, contact, member, content):
        if contact.uin not in logs:
            logs[contact.uin] = {
                'content': None,
                'count': 1,
                'last': None
            }
        log = logs[contact.uin]
        if content == log['last']:
            return
        if log['content'] == content:
            log['count'] += 1
            if log['count'] == 3:
                bot.SendTo(contact, '喵喵喵！' + content)
                log['last'] = content
        else:
            log['content'] = content
            log['count'] = 1
