import string
import random
from .utils import jsonload, textload

_weapons = jsonload('data/weapons.json')
_subweapons = jsonload('data/subweapons.json')
_specials = jsonload('data/specials.json')
_mains = jsonload('data/mains.json')
_weapon_list = textload('data/weapon_list.txt').split('\n')[:-1]

_weapons_scroll = [x for x in _weapon_list if _weapons[x]['Level Unlocked'].find('Scroll') >= 0]
_weapons_amiibo = [x for x in _weapon_list if _weapons[x]['Level Unlocked'].find('Amiibo') >= 0]

_LETTERNUMBERS = string.ascii_letters + string.digits


def _get_weapon_name(weapon, lang, alias):
    if lang == 'en' or lang == 'jp':
        return weapon[lang]
    if alias:
        al = weapon.get('alias')
        if al:
            return al
    name = weapon.get('zh')
    if name:
        return name
    subname = _subweapons[weapon['Sub Weapon']]['zh']
    mainname = _mains[weapon['main']]['zh']
    if mainname[0] in _LETTERNUMBERS:
        subname += ' '
    return subname + mainname


def get_random_weapons(scroll=True, amiibo=False, number=1, lang='zh', alias=False):
    ret = []
    for i in range(number):
        while True:
            weapon = random.sample(_weapon_list, 1)[0]
            if not scroll and weapon in _weapons_scroll:
                continue
            if not amiibo and weapon in _weapons_amiibo:
                continue
            name = _get_weapon_name(_weapons[weapon], lang, alias)
            if name in ret:
                continue
            ret.append(name)
            break
    return ret


def get_weapon_details(weapon_name, lang='zh', alias=False):
    for each in _weapon_list:
        if _weapons[each][lang] == weapon_name or \
                alias and weapon_name == _weapons[each]['alias']:
            return _weapons[each]
    return None

