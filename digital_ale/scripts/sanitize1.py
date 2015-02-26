#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import transaction


from sqlalchemy import (
    engine_from_config,
    )

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from digital_ale.models import (
    DBSession,
    Concept,
    PlaceOfInquiry,
    SheetEntry
    )

from digital_ale.sheet_parser import SheetParser, initial_clean_up

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini')
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    with transaction.manager:
        places = DBSession.query(PlaceOfInquiry).all()
        parser = SheetParser(places)
        entries = DBSession.query(SheetEntry).order_by(SheetEntry.id).all()
        for e in entries:
            new_data = initial_clean_up(SheetEntry.replace_escape_sequences(e.data))
            if e.data != new_data:
                e.data = new_data
                e.extract_data(parser)

if __name__ == '__main__':
    main()
