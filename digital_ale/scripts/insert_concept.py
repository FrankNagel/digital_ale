#!/usr/bin/env python
# -*- coding: utf8 -*-

#http://www.artandlogic.com/blog/2013/03/confused-by-dbsession-in-pyramid/

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
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <number> <concept fra> <concept eng>\n'
          '(example: "%s development.ini 2 \'(le soleil) se lève\' \'(the sun) rises\'")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 5:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    #Base.metadata.create_all(engine)
    argv = map(lambda x: unicode(x, 'utf8'), argv)
    with transaction.manager:
        nr = int(argv[2])
        c = DBSession.query(Concept).filter(Concept.id == nr).first()
        if c == None:
            c = Concept()
            c.id = nr
            DBSession.add(c)
        else:
            print >> sys.stderr, 'Redefining concept', nr
        c.fra = argv[3]
        c.eng = argv[4]

if __name__ == '__main__':
    main()
