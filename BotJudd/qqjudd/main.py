from .bases import BaseAction
from .stage_info import StageInfo
from .weapon_info import WeaponInfo
from .private_room import PrivateRoom
from .gossip import Gossip

actions = {
    StageInfo, WeaponInfo, PrivateRoom, Gossip
}

sessions = set()

def onQQMessage(bot, contact, member, content):
    p = None
    content, lang = BaseAction.check_handle(bot, contact, member, content)
    if content is None:
        return
    handled = False
    to_discard = None
    for session in sessions:
        ret = session.handle_next(bot, contact, member, content, lang)
        if ret is not None:
            if not ret:
                to_discard = session
            handled = True
            break
    if to_discard is not None:
        sessions.discard(to_discard)
    if handled:
        return

    for action in actions:
        p = action.check_handle(bot, contact, member, content, lang)
        if p is not None:
            break
    if p is None:
        bot.SendTo(contact, '@' + member.name + '\n听不懂你在说什么')
        return
    if p is not None:
        if bot.conf.debug:
            ret = p.handle()
            if ret is not None:
                sessions.add(ret)
        else:
            try:
                ret = p.handle()
                if ret is not None:
                    sessions.add(ret)
            except:
                bot.SendTo(contact, '@' + member.name + '\n发生了错误')
