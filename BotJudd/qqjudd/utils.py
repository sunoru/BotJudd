_CHNUMBERS = {
    '零': 0,
    '一': 1,
    '二': 2,
    '两': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9,
    '十': 10,
    '十一': 11,
    '十二': 12
}

def parse_number(numstr):
    try:
        return int(numstr)
    except ValueError:
        return _CHNUMBERS.get(numstr)


_SYMBOLS = {
    '?', '？', '。', '.', ',', '，', '!', '！'
}

def strip(content):
    while content and content[-1] in _SYMBOLS:
        content = content[:-1].strip()
    return content
