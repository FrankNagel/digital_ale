#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import os
import re
import logging
import transaction


from sqlalchemy import (
    engine_from_config,
    )

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from digital_ale.models import (
    DBSession,
    PlaceOfInquiry,
    SheetEntry
    )

from digital_ale.sheet_parser import SheetParser, initial_replacements

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [replacement_set..]\n'
          '(example: "%s development.ini 0 1' % cmd)
    sys.exit(1)

def make_replacements(data, selection):
    result = []
    state = 0
    regex = re.compile(r'\s*\(\s*(\d)\.?\s*([^\W\d_]+)\)\s*')
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
                if len(parts) < 2:
                    log.warn('Ignoring inconsistent line\n\t' + line)
                    result.append(line)
                    continue
                parts[1] = initial_replacements(parts[1], selection)
                result.append('\t'.join(parts))
    return '\n'.join(result)

def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    if len(argv) == 2:
        selection = None
    else:
        selection = map(int, argv[2:])
    with transaction.manager:
        places = DBSession.query(PlaceOfInquiry).all()
        parser = SheetParser(places)
        entries = DBSession.query(SheetEntry).order_by(SheetEntry.id).all()
        for index, e in enumerate(entries):
            new_data = make_replacements(e.data, selection)
            if e.data != new_data:
                e.data = new_data
                e.extract_data(parser)

if __name__ == '__main__':
    main()
