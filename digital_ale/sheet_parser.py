# -*- coding: utf-8 -*-

import re
import logging
import unicodedata
import HTMLParser
import models

log = logging.getLogger(__name__)

unescape = HTMLParser.HTMLParser().unescape

replacements_1 = [
    (u'\u0332', u'\u0331'), # COMBINING LOW LINE -> U+0331	COMBINING MACRON BELOW
    (u'\u0342', u'\u0311'), # COMBINING GREEK PERISPOMENI -> U+0311	COMBINING INVERTED BREVE
    (u'\u0338', u'\u0337'), # COMBINING LONG SOLIDUS OVERLAY -> U+0337	COMBINING SHORT SOLIDUS OVERLAY
    (u'\u0327', u'\u0329'), # COMBINING CEDILLA -> U+0329	COMBINING VERTICAL LINE BELOW
    (u'\u0312', u'\u0301'), # COMBINING TURNED COMMA ABOVE -> U+0301	COMBINING ACUTE ACCENT
    (u'\u1DC6', u'\u2019'), # COMBINING MACRON-GRAVE -> U+2019	RIGHT SINGLE QUOTATION MARK
    (u'\u032A', u'\u032F'), # COMBINING BRIDGE BELOW -> U+032F	COMBINING INVERTED BREVE BELOW
    (u'\u0317', u'\u0329'), # COMBINING ACUTE ACCENT BELOW -> U+0329	COMBINING VERTICAL LINE BELOW
    (u'\u0320', u'\u0331'), # COMBINING MINUS SIGN BELOW -> U+0331	COMBINING MACRON BELOW
    (u'\u0336', u'\u0335'), # COMBINING LONG STROKE OVERLAY -> U+0335	COMBINING SHORT STROKE OVERLAY
    (u'\u0305', u'\u0335'), # COMBINING OVERLINE -> U+0335	COMBINING SHORT STROKE OVERLAY
    (u'\u0322', u'\u0329'), # COMBINING RETROFLEX HOOK BELOW -> U+0329	COMBINING VERTICAL LINE BELOW
    (u'\u0326', u'\u0329'), # COMBINING COMMA BELOW -> U+0329	COMBINING VERTICAL LINE BELOW
    (u'\u0330', u'\u0331'), # COMBINING TILDE BELOW -> U+0331	COMBINING MACRON BELOW
    (u'\u0339', u'\u0329'), # COMBINING RIGHT HALF RING BELOW -> U+0329	COMBINING VERTICAL LINE BELOW
    (u'\u0358', u'\u0307'), # COMBINING DOT ABOVE RIGHT -> U+0307	COMBINING DOT ABOVE
    (u'\u0360', u'\u035E'), # COMBINING DOUBLE TILDE -> U+035E	COMBINING DOUBLE MACRON
    (u'\u05B4', u'\u0323'), # HEBREW POINT HIRIQ -> U+0323	COMBINING DOT BELOW
    (u'\u002D', u'\u0020'), # HYPHEN-MINUS -> U+0020	SPACE
    (u'\u2013', u'\u0020'), # EN DASH -> U+0020	SPACE
    (u'\u00B7', u'\u002E'), # MIDDLE DOT -> U+002E	FULL STOP
    (u'\u02C8', u'\u0027'), # MODIFIER LETTER VERTICAL LINE -> U+0027	APOSTROPHE
    (u'\u2205', u'\u00F8'), # EMPTY SET -> U+00F8	LATIN SMALL LETTER O WITH STROKE
    (u'\u2206', u'\u25B3'), # INCREMENT -> U+25B3	WHITE UP-POINTING TRIANGLE
    (u'\u03F6', u'\u025C'), # GREEK REVERSED LUNATE EPSILON SYMBOL -> U+025C	LATIN SMALL LETTER REVERSED OPEN E
    (u'\u007E', u''), # TILDE -> KOMMA + SPACE
    (u'\u0033', u'\u025C'), # DIGIT THREE -> U+025C	LATIN SMALL LETTER REVERSED OPEN E
    (u'\u1D00', u'\u0041'), # LATIN LETTER SMALL CAPITAL A -> U+0041	LATIN CAPITAL LETTER A
    (u'\u0042', u'\u03B2'), # LATIN CAPITAL LETTER B -> U+03B2	GREEK SMALL LETTER BETA
    (u'\u0183', u'\u0062\u0304'), # LATIN SMALL LETTER B WITH TOPBAR -> U+0062 LATIN SMALL LETTER B + U+0304 COMBINING MACRON
    (u'\u018C', u'\u0064\u0304'), # LATIN SMALL LETTER D WITH TOPBAR -> U+0064 LATIN SMALL LETTER D + U+0304 COMBINING MACRON
    (u'\u1D07', u'\u0045'), # LATIN LETTER SMALL CAPITAL E -> U+0045	LATIN CAPITAL LETTER E
    (u'\u0259', u'\u01DD'), # LATIN SMALL LETTER SCHWA -> U+01DD LATIN SMALL LETTER TURNED E
    (u'\u025B', u'\u03B5'), # LATIN SMALL LETTER OPEN E -> U+03B5	GREEK SMALL LETTER EPSILON
    (u'\u1D4B', u'\u03B5'), # MODIFIER LETTER SMALL OPEN E -> U+03B5	GREEK SMALL LETTER EPSILON
    (u'\u0194', u'\u0263'), # LATIN CAPITAL LETTER GAMMA -> U+0263 LATIN SMALL LETTER GAMMA
    (u'\u02BB', u'\u2019'), # MODIFIER LETTER TURNED COMMA -> U+2019	RIGHT SINGLE QUOTATION MARK
    (u'\u0049', u'\u0131'), # LATIN CAPITAL LETTER I -> U+0131	LATIN SMALL LETTER DOTLESS I
    (u'\u026A', u'\u0131'), # LATIN LETTER SMALL CAPITAL I -> U+0131	LATIN SMALL LETTER DOTLESS I
    (u'\u0197', u'\u0268'), # LATIN CAPITAL LETTER I WITH STROKE -> U+0268	LATIN SMALL LETTER I WITH STROKE
    (u'\u0269', u'\u0069'), # LATIN SMALL LETTER IOTA -> U+0069 LATIN SMALL LETTER I
    (u'\u004A', u'\u0237'), # LATIN CAPITAL LETTER J -> U+0237	LATIN SMALL LETTER DOTLESS J
    (u'\u0248', u'\u0249'), # LATIN CAPITAL LETTER J WITH STROKE -> U+0249	LATIN SMALL LETTER J WITH STROKE
    (u'\u025F', u'\u0249'), # LATIN SMALL LETTER DOTLESS J WITH STROKE -> U+0249	LATIN SMALL LETTER J WITH STROKE
    (u'\u004B', u'\u006B'), # LATIN CAPITAL LETTER K -> U+006B	LATIN SMALL LETTER K
    (u'\u2113', u'\u006C'), # SCRIPT SMALL L -> U+006C	LATIN SMALL LETTER L
    (u'\u004C', u'\u006C'), # LATIN CAPITAL LETTER L -> U+006C	LATIN SMALL LETTER L
    (u'\u02E1', u'\u0027'), # MODIFIER LETTER SMALL L -> U+0027	APOSTROPHE
    (u'\u019A', u'\u0142'), # LATIN SMALL LETTER L WITH BAR -> U+0142	LATIN SMALL LETTER L WITH STROKE
    (u'\u026B', u'\u0142'), # LATIN SMALL LETTER L WITH MIDDLE TILDE -> U+0142	LATIN SMALL LETTER L WITH STROKE
    (u'\u026C', u'\u0142'), # LATIN SMALL LETTER L WITH BELT -> U+0142	LATIN SMALL LETTER L WITH STROKE
    (u'\u004D', u'\u006D'), # LATIN CAPITAL LETTER M -> U+006D LATIN SMALL LETTER M
    (u'\u004E', u'\u006E'), # LATIN CAPITAL LETTER N -> U+006E	LATIN SMALL LETTER N
    (u'\u019E', u'\u014B'), # LATIN SMALL LETTER N WITH LONG RIGHT LEG -> U+014B LATIN SMALL LETTER ENG
    (u'\u004F', u'\u006F'), # LATIN CAPITAL LETTER O -> U+006F LATIN SMALL LETTER O
    (u'\u00D8', u'\u00F8'), # LATIN CAPITAL LETTER O WITH STROKE -> U+00F8	LATIN SMALL LETTER O WITH STROKE
    (u'\u0186', u'\u0254'), # LATIN CAPITAL LETTER OPEN O -> U+0254	LATIN SMALL LETTER OPEN O
    (u'\u0050', u'\u0070'), # LATIN CAPITAL LETTER P -> U+0070	LATIN SMALL LETTER P
    (u'\u0280', u'\u0052'), # LATIN LETTER SMALL CAPITAL R -> U+0052	LATIN CAPITAL LETTER R
    (u'\u0053', u'\u0073'), # LATIN CAPITAL LETTER S -> U+0073 LATIN SMALL LETTER S
    (u'\u02E2', u'\u0073'), # MODIFIER LETTER SMALL S -> U+0073 LATIN SMALL LETTER S
    (u'\u017F', u'\u0283'), # LATIN SMALL LETTER LONG S -> U+0283	LATIN SMALL LETTER ESH
    (u'\u00DF', u'\u03B2'), # LATIN SMALL LETTER SHARP S -> U+03B2	GREEK SMALL LETTER BETA
    (u'\u02AE', u'\u0265'), # LATIN SMALL LETTER TURNED H WITH FISHHOOK -> U+0265	LATIN SMALL LETTER TURNED H
    (u'\u0056', u'\u0076'), # LATIN CAPITAL LETTER V -> U+0076	LATIN SMALL LETTER V
    (u'\u028B', u'\u0076'), # LATIN SMALL LETTER V WITH HOOK -> U+0076	LATIN SMALL LETTER V
    (u'\u0057', u'\u0077'), # LATIN CAPITAL LETTER W -> U+0077	LATIN SMALL LETTER W
    (u'\u0058', u'\u0078'), # LATIN CAPITAL LETTER X -> U+0078	LATIN SMALL LETTER X
    (u'\u0059', u'\u0079'), # LATIN CAPITAL LETTER Y -> U+0079	LATIN SMALL LETTER Y
    (u'\u005A', u'\u007A'), # LATIN CAPITAL LETTER Z -> U+007A	LATIN SMALL LETTER Z
    (u'\u1D8E', u'\u0292'), # LATIN SMALL LETTER Z WITH PALATAL HOOK -> U+0292	LATIN SMALL LETTER EZH
    (u'\u0225', u'\u0292'), # LATIN SMALL LETTER Z WITH HOOK -> U+0292	LATIN SMALL LETTER EZH
    (u'\u01B7', u'\u0292'), # LATIN CAPITAL LETTER EZH -> U+0292	LATIN SMALL LETTER EZH
    (u'\u02BC', u'\u2019'), # MODIFIER LETTER APOSTROPHE -> U+2019	RIGHT SINGLE QUOTATION MARK
    (u'\u02BE', u'\u1D53'), # MODIFIER LETTER RIGHT HALF RING -> U+1D53 MODIFIER LETTER SMALL OPEN O
    (u'\u02BF', u'\u2019'), # MODIFIER LETTER LEFT HALF RING -> U+2019	RIGHT SINGLE QUOTATION MARK
    (u'\u03B1', u'\u0061'), # GREEK SMALL LETTER ALPHA -> U+0061	LATIN SMALL LETTER A
    (u'\u03B3', u'\u0263'), # GREEK SMALL LETTER GAMMA -> U+0263	LATIN SMALL LETTER GAMMA
    (u'\u0394', u'\u25B3'), # GREEK CAPITAL LETTER DELTA -> U+25B3	WHITE UP-POINTING TRIANGLE
    (u'\u03B7', u'\u014B'), # GREEK SMALL LETTER ETA -> U+014B LATIN SMALL LETTER ENG
    (u'\u03D1', u'\u03B8'), # GREEK THETA SYMBOL -> U+03B8	GREEK SMALL LETTER THETA
    (u'\u0398', u'\u03B8'), # GREEK CAPITAL LETTER THETA -> U+03B8	GREEK SMALL LETTER THETA
    (u'\u1D27', u'\u028C'), # GREEK LETTER SMALL CAPITAL LAMDA -> U+028C	LATIN SMALL LETTER TURNED V
    (u'\u037B', u'\u0254'), # GREEK SMALL REVERSED LUNATE SIGMA SYMBOL -> U+0254	LATIN SMALL LETTER OPEN O
    (u'\u03D2', u'\u0263'), # GREEK UPSILON WITH HOOK SYMBOL -> U+0263 LATIN SMALL LETTER GAMMA
    (u'\u03C7', u'\u0078'), # GREEK SMALL LETTER CHI -> U+0078	LATIN SMALL LETTER X
    (u'\u03A7', u'\u0078'), # GREEK CAPITAL LETTER CHI -> U+0078	LATIN SMALL LETTER X
    (u'\u03C9', u'\u0077'), # GREEK SMALL LETTER OMEGA -> U+0077	LATIN SMALL LETTER W
    (u'\u04E1', u'\u0292'), # CYRILLIC SMALL LETTER ABKHASIAN DZE -> U+0292	LATIN SMALL LETTER EZH
    (u'\u0408', u'\u0237'), # CYRILLIC CAPITAL LETTER JE -> U+0237	LATIN SMALL LETTER DOTLESS J
    (u'\u0443', u'\u0079'), # CYRILLIC SMALL LETTER U -> U+0079	LATIN SMALL LETTER Y
]

replacements_2 = [
    (u'\u0063\u0329', u'\u00E7',), # LATIN SMALL LETTER C, COMBINING VERTICAL LINE BELOW -> U+00E7 LATIN SMALL LETTER C WITH CEDILLA
]

replacements = [replacements_1, replacements_2]

def initial_replacements(pronounciation, selection=None):
    if selection is None:
        selection = range(len(replacements))
    pronounciation = unicodedata.normalize('NFD', pronounciation)
    for index in selection:
        for source, dest in replacements[index]:
            pronounciation = pronounciation.replace(source, dest)
    pronounciation = unicodedata.normalize('NFC', pronounciation)
    return pronounciation

def initial_clean_up(data):
    if type(data) != unicode:
        data = unicode(data, 'utf8')
    result = []
    state = 0
    regex = re.compile(r'\s*\(\s*(\d)\.?\s*([^\W\d_]+)\)\s*')
    of_regex = re.compile(r'\s*[[(]?\s*(?:[oO]\.\s*[fF]\.|[fF]\.\s*[oO]\.)') # 'original form' artefacts
    for line in data.splitlines():
        if state == 0:
            match = regex.match(line)
            if match and match.group(2).upper() == 'DATA':
                state = 1
            result.append(line)
        elif state == 1:
            if not line.strip() or line.strip().upper() in  ['NV', 'NL']:
                result.append(line)
                continue
            match = regex.match(line)
            if match:
                state = 0
                result.append(line)
            else:
                parts = line.split('\t')
                if len(parts) < 4:
                    parts.insert(2, '')
                if len(parts) < 4:
                    log.warn('Ignoring inconsistent line\n\t' + line)
                    result.append(line)
                    continue
                pron = parts[1]
                of_match = of_regex.search(pron)
                if of_match:
                    parts[1] = pron[:of_match.start()]
                    parts[2] = pron[of_match.start():].lstrip() + parts[2]
                    log.info('shifting right: "%s"' % pron[of_match.start():])
                parts[1] = initial_replacements(parts[1])
                parts[1] = clean_up_underline(parts[1])
                result.append('\t'.join(parts))
        else:
            break
    return '\n'.join(result)


def clean_up_underline(data):
    underline_regex = re.compile('<u>(.*?)</u>')
    start = 0
    while True:
        match = underline_regex.search(data, start)
        if not match:
            break
        graphemes = build_graphemes(match.group(1))
        if len(graphemes) == 2:
            old_data = data
            data = data[:match.start()] + graphemes[0] + unichr(0x035f) + graphemes[1] + data[match.end():]
            log.info('replacing "%s" with "%s"' % (old_data, data))
        start = match.start() + 1
    return data

def build_graphemes(data):
    result = []
    for x in data:
        if unicodedata.combining(x):
            if not result:
                result.append([])
            result[-1].append(x)
        else:
            result.append([x])
    return [u''.join(x) for x in result]

class LineIterator():
    def __init__(self, text):
        self.text = text.splitlines()
        self.index = 0

    def peek(self):
        while self.index < len(self.text) and not self.text[self.index].strip():
            self.index += 1
        if self.index >= len(self.text):
            return self.index+1, ''
        return self.index+1, self.text[self.index]

    def next(self):
        t = self.peek()
        self.index += 1
        return t

aliases = {
    ('05.0','021'): '05.0.301',

    ('07.0','301'): '07.F.301',
    ('07.0','302'): '07.F.302',
    ('07.0','351'): '07.F.351',
    ('07.0','352'): '07.F.352',
    ('07.0','353'): '07.F.353',
    ('07.0','354'): '07.F.354',
    ('07.0','355'): '07.F.355',
    ('07.0','356'): '07.F.356',
    ('07.0','357'): '07.F.357',
    ('07.0','358'): '07.F.358',
    ('07.0','359'): '07.F.359',
    ('07.0','360'): '07.F.360',
    ('07.0','361'): '07.F.361',
    ('07.0','362'): '07.F.362',
    ('07.0','363'): '07.F.363',
    ('07.0','391'): '07.F.391',
    ('07.0','392'): '07.F.392',
    ('07.0','393'): '07.F.393',
    ('07.0','401'): '07.F.401',
    ('07.0','701'): '07.F.701',
    ('07.0','702'): '07.F.702',


    ('08.0','301'): '25.2.208',

    ('18.0','101'): '18.1.101',
    ('18.0','102'): '18.1.102',
    ('18.0','103'): '18.1.103',
    ('18.0','104'): '18.1.104',
    ('18.0','105'): '18.1.105',
    ('18.0','801'): '08.0.801',

    ('22.0','001'): '18.1.201',
    ('22.0','002'): '18.1.202',
    ('22.0','003'): '18.1.203',
    ('22.0','137'): '18.1.204',

    ('24.0','501'): '07.5.501',
    ('24.0','502'): '07.5.502',
    ('24.0','503'): '07.5.503',
    ('24.0','504'): '07.5.504',
    ('24.0','505'): '07.5.505',
    ('24.0','506'): '07.5.506',

    ('29.0','101'): '29.1.101',
    ('29.0','102'): '29.1.102',
    ('29.0','103'): '29.1.103',
    ('29.0','104'): '29.1.104',
    ('29.0','105'): '29.1.105',
    ('29.0','106'): '29.1.106',
    ('29.0','107'): '29.1.107',
}

class SheetParser(object):
    def __init__(self, places):
        self.places = places
        self.places_pc_old = {p.pointcode_old: p  for p in places}
        
        self.part_regex = re.compile(r'\s*\(\s*(\d)\.?\s*([^\W\d_]+)\)\s*')
        self.result = []
        self.messages = []
        self.context = ''

    def parse(self, sheetEntry):
        self.result = []
        self.messages = []
        lines = LineIterator(sheetEntry.data)
        context_from_id = sheetEntry.id[4:8]
        state = 0
        result = []
        while True:
            nr, line = lines.next()
            if not line:
                break
            match = self.part_regex.match(line)
            if state == 0:
                if match and match.group(2).upper() == 'IDENT':
                    state = 1
                    self.parseIdent(lines, context_from_id)
                    continue
            elif state == 1:
                if match and match.group(2).upper() == 'DATA':
                    state = 0
                    self.parse_data(lines, sheetEntry)
        sheetEntry.parser_messages = ''.join(self.messages)
        return self.result

    def parseIdent(self, lines, context_from_id):
        nr, line = lines.next()
        if not line:
            return
        start = 0

        while start < len(line):
            if line[start] in '0123456789':
                break
            start += 1
        end = start
        while end < len(line):
            if line[end] not in '.0123456789':
                break
            end += 1
        context = line[start:end]
        if context == '14.601':
            context = '14.6'
        if context and context[-1] == '.':
            context = context[:-1]
        if len(context) == 3 and '.' not in context:
            context = context[:2] + '.' + context[2]
        if '.' not in context:
            context = context + '.0'
        if not (len(context) == 4 and context[0].isdigit() and context[1].isdigit() and context[3].isdigit()
                and context[2] == '.'):
            self.messages.extend(['Unable to determine IDENT; chosing from name: %s\n' % context_from_id, '\n'])
            context = context_from_id
        self.context = context
        while True:
            nr, line = lines.peek()
            if not line or self.part_regex.match(line):
                return
            lines.next()


    def parse_data(self, lines, sheetEntry):
        while True:
            nr, line = lines.peek()
            if not line or self.part_regex.match(line):
                return
            lines.next()
            parts = line.split('\t')
            if len(parts) == 3:
                parts.insert(2, '')
            if len(parts) not in (4,5):
                if line.strip().upper() not in  ['NV', 'NL']:
                    self.messages.extend(['Line %i: %s\n' % (nr, line),
                                          'Expecting three to five TAB separated fields (got %i)\n' % len(parts), '\n'])
                continue
            if self.context == '14.7' and parts[3] == '' and parts[0].strip() in ['601', '701', '702']:
                parts[3] = parts[0]
                parts[0] = ''
                self.messages.extend(['Line %i: %s\n' % (nr, line),
                                      'Interpreting first field as place code.\n', '\n'])
            #strip <u> tag surrounding the grouping code
            parts[0] = parts[0].strip()
            if parts[0].startswith('<u>') and parts[0].endswith('</u>'):
                parts[0] = parts[0][3:-4]
            parts[1] = parts[1].strip()
            if parts[1] in (u'Ø', u'ø'):
                continue
            if not parts[1] and parts[3].strip():
                pronounciation = ''
                self.messages.extend(['Line %i: %s\n' % (nr, line), 'Warning: Empty pronounciation field.\n\n'])
            else:
                pronounciation = unescape(parts[1])
            if '@' in pronounciation or '?' in pronounciation:
                self.messages.extend(['Line %i: %s\n' % (nr, line),
                                      'Unexpected character (@ or ?) in pronounciation "%s"\n' % pronounciation,
                                      '\n'])
            try:
                observations = self.parse_places(parts[3], (nr, line))
            except Exception, e:
                observations = []
                self.messages.extend(['Line %i: %s\n' % (nr, line), 'Exception parsing place numbers: %s\n' % e , '\n'])
            
            if observations:
                pron_parts = pronounciation.split(',')
                for p in pron_parts:
                    p = p.strip()
                    if not p:
                        p = 'Not Available'
                    #strip surrounding <u> tag from pronounciation
                    if p.startswith('<u>') and p.endswith('</u>') and p.find('<u>', 1) == -1:
                        p = p[3:-4]
                    pron = models.Pronounciation()
                    pron.sheet_entry_fkey = sheetEntry.id
                    pron.grouping_code = parts[0]
                    pron.pronounciation = p
                    pron.comment = parts[2]
                    pron.observations.extend(observations)
                    self.result.append(pron)


    def parse_places(self, places, parse_context):
        if '@' in places or '?' in places:
            self.messages.extend(['Line %i: %s\n' % parse_context,
                                  'Unexpected character (@ or ?) in placenumbers\n',
                                  '\n'])

        result_numbers = []
        have_range = False
        index = 0
        place_def = []
        underline = False

        places += ' ' # make sure, to clear out the result_numbers in the end
        while index < len(places) and index != -1:
            if places[index:index+3] == '<u>':
                underline = True
                index += 3
            elif places[index:index+3] == '</u>':
                underline = False
                index += 4
            elif places[index].isdigit():
                place_def.extend(places[index])
                index += 1
            else:
                if place_def:
                    n = int(''.join(place_def))
                    place_def = []
                    if have_range:
                        for x in xrange(result_numbers[-1][0]+1, n):
                            result_numbers.append((x, underline, True))
                        result_numbers.append((n, underline, False))
                        have_range = False
                    else:
                        result_numbers.append((n, underline, False))
                if places[index] == '-' and result_numbers:
                    have_range = True
                index += 1

        result = []
        seen = set()
        for n, _, quiet in result_numbers:
            if n in seen:
                self.messages.extend(['Line %i: %s\n' % parse_context, 'Duplicate place number: %i\n' % n, '\n'])
                continue
            seen.add(n)
            place = self.find_place(n, parse_context, quiet)
            if place:
                result.append(place)
        return result


    def find_place(self, num, parse_context, quiet=False):
        num = '%03i' % num
        key = self.context + '.' + num
        if not self.places_pc_old.has_key(key):
            if aliases.has_key((self.context, num)):
                return self.places_pc_old[aliases[(self.context, num)]]
            if not quiet:
                self.messages.extend(['Line %i: %s\n' % parse_context, 'Could not find place for: %s\n' % num , '\n'])
        else:
            return self.places_pc_old[key]
