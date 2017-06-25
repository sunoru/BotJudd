import datetime
import re
from BotJudd import splatoon
from .bases import BaseAction
from .utils import parse_number


def _check_handle_time(content, **kwargs):
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


def _check_handle_random(content, **kwargs):
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


def _get_message(stage_info):
    return '%s：%s' % (
        stage_info['mode'], ' 和 '.join(stage_info['maps'])
    )


def _current_stages(method):
    def update_message(self):
        stages = method(False, self.lang)
        if isinstance(stages, list):
            self.messages = [_get_message(x) for x in stages]
        else:
            self.messages = [_get_message(stages)]
    return update_message


def _today_stages():
    def update_message(self):
        stages = method(lang=self.lang, **kwargs)
        self.messages = [
            '\n'.join([' - '.join(p[x].strftime('%Y/%m/%d %H:%M') for x in ['startTime', 'endTime']),
                _get_message(p['stages'][0]), _get_message(p['stages'][1])])
            for p in stages
        ]
    return update_message


def _random_stages():
    def update_message(self):
        n = self.args
        if not n or n > 12:
            self.messages = ['一次最多生成 12 张图']
        else:
            self.messages = ['%s：%s' % (x['mode'], x['map']) for x in splatoon.get_random_stages(True, n, self.lang)]
    return update_message


def _sometime_stages():
    def update_message(self):
        t = self.args
        self.messages = [t.strftime('%Y/%m/%d %H:00') + ' 后的图为：']
        stages = splatoon.get_sometime_stages(t, False, self.lang)
        if stages is None:
            self.messages.append('现在还不知道啦')
        else:
            for x in stages:
                self.messages.append(_get_message(x))
    return update_message


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
    command_list = BaseAction.make_commands([
        [r'^(/currentstages|现在什么图)$', 'currentstages', _current_stages(splatoon.get_current_stages)],
        [r'^(/currentturfstages|现在涂地什么图)$', 'currentturfstages', _current_stages(splatoon.get_current_turf_stages)],
        [r'^(/currentrankedstages|现在真格什么图)$', 'currentrankedstages',
            _current_stages(splatoon.get_current_ranked_stages)],
        [r'^(/todaystages|今天什么图)$', 'todaystages', _today_stages()],
        [_check_handle_random, 'randomstages', _random_stages()],
        [_check_handle_time, 'sometimestages', _sometime_stages()],
    ])

    def __init__(self, command, bot, contact, member, content, lang, args):
        super().__init__(command, bot, contact, member, content, lang, args)
        self.messages = None

    def handle(self):
        t = super().handle()
        if self.messages:
            self.sendMessage('\n'.join(self.messages))
        return t
