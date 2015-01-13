#!/usr/bin/env python
"""
One time script to import Places of Inquiry from a pickle file into the database.
"""

import os, os.path
import shutil
import sys
import transaction
import pickle
import json
import pprint
import traceback
from collections import namedtuple
from sqlalchemy import (
    engine_from_config,
    and_,
    )
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
from pyramid.scripts.common import parse_vars
from pyramid.path import AssetResolver
from digital_ale.models import (
    CandidateSource,
    DBSession,
    PlaceOfInquiry,
    PlaceCandidate
    )


Geolocation = namedtuple('Geolocation', ['row', 'source', 'status_code', 'response'])

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <filename>\n'
          '(example: "%s development.ini places.pickle")' % (cmd, cmd))
    sys.exit(1)

def parse_response(geolocation):
    payload = json.loads(geolocation.response)
    if geolocation.source == CandidateSource.google:
        return PlaceCandidate.parse_response_google(payload)
    elif geolocation.source == CandidateSource.geonames:
        return PlaceCandidate.parse_response_geonames(payload)
    else:
        print >> sys.stderr, 'unknown source:', geolocation.source
        return None


def main(argv=sys.argv):
    global settings
    global resolver

    if len(argv) < 2:
        usage(argv)
        sys.exit(1)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    resolver = AssetResolver('digital_ale')
    engine = engine_from_config(settings, 'sqlalchemy.')

    DBSession.configure(bind=engine)

    #make sure Geolocation is available for pickle
    if not hasattr(sys.modules['__main__'], 'Geolocation'):
        sys.modules['__main__'].__dict__['Geolocation'] = Geolocation

    with open(argv[2], 'rb') as dump:
        places = pickle.load(dump)

    with transaction.manager:
        for p in places:
            place = PlaceOfInquiry()
            place.pointcode_old = p.row[0]
            place.pointcode_new = p.row[1]
            place.language_group = p.row[2]
            place.name = p.row[3].replace('_', ' ')
            DBSession.add(place)
            DBSession.flush()
            assert place.id != None
            candidates = parse_response(p)

            #hard requirement: geographic location somewhere in europe
            filtered = [c for c in candidates if 34 < c.lat < 71.2 and -25 < c.lng < 62]
            if not filtered and candidates:
                print >> sys.stderr, place.name, place.pointcode_old, 'all results outside BB'
                for c in candidates:
                    print c.complete_data
            candidates = filtered

            #soft requirements: filter as long as alternatives remain
            country = place.pointcode_new[:2]
            filters = [lambda x: x.name == place.name,
                       lambda x: x.country_code == country, #sometimes wrong, i.e. for channel islands
                       lambda x: x.feature_code == 'locality,political' or x.feature_code.startswith('PPL')]
            for f in filters:
                filtered = [c for c in candidates if f(c)]
                if filtered:
                    candidates = filtered
            if not candidates:
                print >> sys.stderr, "no candidate for %s in '%s' found." % (place.name, country)
#                for c in candidates['results']:
#                    print >> sys.stderr, '   ', c['formatted_address'].encode('utf8')
            for c in candidates:
                c.place_of_inquiry_fkey = place.id
                DBSession.add(c)
            if len(candidates) == 1:
                place.lat = candidates[0].lat
                place.lng = candidates[0].lng
if __name__ == '__main__':
    main()
