import re
from BotJudd import splatoon
from .bases import BaseAction
from .utils import strip


def _check_handle_random(content, **kwargs):
    amiibo = False
    scroll = True
    if content.startswith('/randomprivateroom'):
        p = strip(content[18:])
        if not p:
            return [], amiibo, scroll
        p = p.split()
        for i in range(1, len(p)):
            if p[i] == 'amiibo':
                amiibo = True
            elif p[i] == 'noscroll':
                scroll = False
            else:
                return None
        return p[0].split(','), amiibo, scroll
    content = strip(content)
    if re.search(r'带\s*Amiibo', content, flags=re.IGNORECASE):
        amiibo = True
        content = re.sub(r'带\s*Amiibo', '', content, flags=re.IGNORECASE)
        content = strip(content)
    if content.find('不带剧情武器') >= 0:
        scroll = False
        content = strip(content.replace('不带剧情武器', ''))
    if content.find('开始随机私房') >= 0:
        content = strip(content.replace('开始随机私房', ''))
    else:
        return None
    if content:
        people = content.split(',')
    else:
        people = []
    return people, amiibo, scroll


def _random_pr():
    def handle(self):
        alive = True
        self.people = self.args[0]
        self.amiibo, self.scroll = self.args[1], self.args[2]
        self.weapons = self.stage = None
        if len(self.people) == 0:
            self.messages = ['有哪些人呢？（用英文逗号隔开）']
            self.status = 1
        elif len(self.people) == 1:
            self.messages = ['一个人无法开始私房呢，还需要加入哪些人呢？（用英文逗号隔开）']
            self.status = 2
        elif len(self.people) > 8:
            self.messages = ['人太多了，重新开房去']
            alive = False
        else:
            self.status = 0
            self.generate_random_weapons()
        self.sendMessage('\n'.join(self.messages))
        return self if alive else None
    return handle


class PrivateRoom(BaseAction):
    help_info = '''
        私房相关：
        开始随机私房
            刷新武器
    '''

    command_list = BaseAction.make_commands([
        [_check_handle_random, 'randompr', _random_pr()],
    ])

    def __init__(self, command, bot, contact, member, content, lang, args):
        super().__init__(command, bot, contact, member, content, lang, args)
        self.status = 0

    def handle(self):
        return super().handle()

    def handle_next(self, bot, contact, member, content, lang):
        if contact.uin != self.contact.uin or member.uin != self.member.uin:
            return None
        alive = None
        if re.search(r'结束私房|不玩了', content):
            self.messages = ['OK，私房结束']
            alive = False
        elif self.status == 1:
            if content:
                self.people = content.split(',')
                self.status = 0
                self.show_people()
            else:
                self.messages = ['加人进私房呀']
            alive = True
        elif self.status == 2:
            for each in content.split(','):
                if each:
                    self.people.append(each)
            self.status = 0
            self.show_people()
            alive = True
        elif re.search(r'^刷新(武器|地图|武器地图|地图武器)$', content):
            self.lang = lang
            self.generate_random_weapons()
            self.show_weapon_stage()
            alive = True
        elif re.search(r'^显示(武器|地图|武器地图|地图武器)$', content):
            self.lang = lang
            self.show_weapon_stage()
            alive = True
        if alive is None:
            q = re.match('^把(.+)换成(.+)$', content)
            if q:
                before, after = (x.strip() for x in q.groups())
                self.messages = [before + ' 没有在私房里呀']
                for i, person in enumerate(self.people):
                    if person == before:
                        self.people[i] = after
                        self.messages = ['私房里的 %s 换成了 %s' % (before, after)]
                alive = True
        if alive is None:
            q = re.match('^(.+)退出私房$', content)
            if q:
                person = q.groups()[0]
                try:
                    self.people.remove(person)
                    self.messages = [person + ' 离开了私房']
                except ValueError:
                    self.messages = [person + ' 没有在私房里呀']
                alive = True
        if alive is None:
            q = re.match('^(.+)进入私房$', content)
            if q:
                people = q.groups()[0].split(',')
                for person in people:
                    self.people.append(person)
                self.show_people()
                alive = True
        if alive is None:
            return None
        if len(self.people) == 1:
            self.messages = ['一个人无法开始私房呢，还需要加入哪些人呢？（用英文逗号隔开）']
            self.status = 2
        elif len(self.people) > 8:
            self.messages = ['人太多了，重新开房去']
            alive = False
        else:
            self.status = 0
        self.sendMessage('\n'.join(self.messages))
        return alive

    def generate_random_weapons(self):
        self.weapons = splatoon.get_random_weapons(self.scroll, self.amiibo, len(self.people), self.lang)
        self.stage = splatoon.get_random_stages(True, 1, self.lang)[0]

    def show_weapon_stage(self):
        if not self.weapons or not self.stage:
            self.generate_random_weapons()
        self.messages = ['%s：%s' % (person, weapon) for person, weapon in zip(self.people, self.weapons)]
        self.messages.insert(0, '%s：%s' % (self.stage['mode'], self.stage['map']))

    def show_people(self):
        self.messages = ['现在私房成员：', '，'.join(self.people)]
