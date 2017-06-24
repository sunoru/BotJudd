import datetime
import re
from BotJudd import splatoon
from .bases import BaseAction
from .utils import parse_number


class StageInfo(BaseAction):
    help_info = '''
        地图相关：
        现在什么图？
        现在涂地什么图？
        现在真格什么图？
        五点后什么图？
        今天什么图？
        随机5张图。
    '''
    def __init__(self, command, bot, contact, member, lang, **kwargs):
        super().__init__(bot, contact, member, lang)
        self.command = command
        if command == 'currentturfstages':
            self.messages = [StageInfo.get_message(splatoon.get_current_turf_stages(False, lang))]
        elif command == 'currentrankedstages':
            self.messages = [StageInfo.get_message(splatoon.get_current_ranked_stages(False, lang))]
        elif command == 'currentstages':
            self.messages = [StageInfo.get_message(x) for x in splatoon.get_current_stages(False, lang)]
        elif command == 'todaystages':
            stages = splatoon.get_cached_stages(True, lang)
            self.messages = [
                '\n'.join([' - '.join(p[x].strftime('%Y/%m/%d %H:%M') for x in ['startTime', 'endTime']), StageInfo.get_message(p['stages'][0]), StageInfo.get_message(p['stages'][1])]) for p in stages
            ]
        elif command == 'sometimestages':
            t = kwargs['t']
            self.messages = [t.strftime('%Y/%m/%d %H:00') + ' 后的图为：']
            stages = splatoon.get_sometime_stages(t, False, lang)
            if stages is None:
                self.messages.append('现在还不知道啦')
            else:
                for x in stages:
                    self.messages.append(StageInfo.get_message(x))
        elif command == 'randomstages':
            n = kwargs['n']
            if n > 12:
                self.messages = ['一次最多生成 12 张图']
            else:
                self.messages = ['%s：%s' % (x['mode'], x['map']) for x in splatoon.get_random_stages(True, n, lang)]

    def handle(self):
        self.sendMessage('\n'.join(self.messages))
        return None

    @staticmethod
    def get_message(stage_info):
        return '%s：%s' % (
            stage_info['mode'], ' 和 '.join(stage_info['maps'])
        )

    @staticmethod
    def check_handle_time(content):
        if content.startswith('/sometimestages'):
            try:
                return datetime.datetime.strptime(content[15:].strip(), '%Y/%m/%d %H:%M')
            except ValueError:
                return None
        if content.endswith('什么图'):
            tmp = content[:-3]
            if tmp[-2:] == '以后':
                tmp = tmp[:-2]
            elif tmp[-1] == '后':
                tmp = tmp[:-1]
            if tmp[-1] != '点':
                return None
            tmp = tmp[:-1].strip()
            h = parse_number(tmp)
            if h is None:
                return None
            now = datetime.datetime.now()
            t1 = datetime.datetime(now.year, now.month, now.day, now.hour, 1)
            delta_h = h - t1.hour
            if delta_h <= 0:
                delta_h += 12
            if delta_h <= 0:
                delta_h += 12
            t1 += datetime.timedelta(0, delta_h * 3600)
            return t1
        return None

    @staticmethod
    def check_handle_random(content):
        if content.startswith('/randomstages'):
            try:
                p = content[13:].strip()
                if not p:
                    return 1
                return int(p)
            except ValueError:
                return None
        content = content.strip()
        q = re.match(r'^随机(.*)张图$', content)
        if not q:
            q = re.match(r'^随机地图(.+)张$', content)
        if q:
            p = q.groups()[0]
            if not p:
                return 1
            t = parse_number(p)
            if t is None:
                return 2007012811
            return t
        return None

    @classmethod
    def check_handle(cls, bot, contact, member, content, lang):
        if content == '/currentstages' or content == '现在什么图':
            return cls('currentstages', bot, contact, member, lang)
        elif content == '/currentturfstages' or content == '现在涂地什么图':
            return cls('currentturfstages', bot, contact, member, lang)
        elif content == '/currentrankedstages' or content == '现在真格什么图':
            return cls('currentrankedstages', bot, contact, member, lang)
        elif content == '/todaystages' or content == '今天什么图':
            return cls('todaystages', bot, contact, member, lang)
        t = StageInfo.check_handle_random(content)
        if t is not None:
            return cls('randomstages', bot, contact, member, lang, n=t)
        t = StageInfo.check_handle_time(content)
        if t is not None:
            return cls('sometimestages', bot, contact, member, lang, t=t)
        return None

