from .bases import BaseAction
from .stage_info import StageInfo
from .weapon_info import WeaponInfo
from .private_room import PrivateRoom
from .gossip import Gossip
from .utils import settings


class AdminAction():
    def __init__(self, sessions):
        self.sessions = sessions
        self.bot = None

    def handle(self, bot, contact, member, content):
        if content.startswith('/eval '):
            expr = content[6:].strip()
            bot.SendTo(contact, '执行命令')
            message = eval(expr)
            if message is None:
                message = '空返回'
        else:
            message = '?'
        bot.SendTo(contact, message)
