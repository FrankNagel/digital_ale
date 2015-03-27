# -*- coding: utf-8 -*-

import re
import logging
import unicodedata
import HTMLParser
import models

log = logging.getLogger(__name__)

unescape = HTMLParser.HTMLParser().unescape


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
            if parts[1] in u'Øø':
                continue
            if not parts[1].strip() and parts[3].strip():
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
                        continue
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
