#!/usr/bin/env python
"""
One time script to merge geodata
"""

import os, os.path
import math
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
    text
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


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <filename>\n'
          '(example: "%s development.ini geodaten.ale")' % (cmd, cmd))
    sys.exit(1)

    
def diff(p0x, p0y, p1x, p1y):
    return math.sqrt(abs(p0x-p1x)**2 + abs(p0y-p1y)**2)


def main(argv=sys.argv):
    global settings
    global resolver

    if len(argv) < 3:
        usage(argv)
        sys.exit(1)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    resolver = AssetResolver('digital_ale')
    engine = engine_from_config(settings, 'sqlalchemy.')

    DBSession.configure(bind=engine)

    aliases = {
        '03.2.201': '',
        '03.2.202': '',
        '03.2.203': '',
        '03.2.204': '',
        '03.2.205': '',
        '03.2.206': '',
        '03.2.207': '',
        '03.2.208': '',
        '03.2.209': '',
        '03.2.210': '',
        '03.2.211': '',
        '06.9.951': '08.9.951',
        '06.9.952': '08.9.952',
        '06.9.953': '08.9.953',
        '06.9.954': '08.9.954',
        '06.9.955': '08.9.955',
        '08.5.511': '10.0.511',
        '09.0.292': '08.0.292',
        '09.0.293': '08.0.293',
        '09.3.301': '',
        '09.3.302': '',
        '09.3.303': '12.1.303',
        '09.3.304': '',
        '14.0.401': '08.0.401',
        '14.0.402': '08.0.402',
        '14.0.403': '08.0.403',
        '14.0.404': '08.0.404',
        '14.0.405': '08.0.405',
        '14.0.406': '08.0.406',
        '14.0.407': '08.0.407',
        '14.0.501': '10.0.501',
        '14.0.502': '10.0.502',
        '14.2.201': '',
        '14.2.202': '',
        '14.2.203': '',
        '14.6.602': '07.5.602',
        '17.2.201': '24.8.201',
        '17.2.202': '24.8.202',
        '17.2.203': '24.8.203',
        '17.9.923': '07.9.923',
        '17.9.924': '07.9.924',
        '17.9.925': '07.9.925',
        '17.9.926': '07.9.926',
        '17.9.927': '07.9.927',
        '17.9.928': '07.9.928',
        '17.9.929': '07.9.929',
        '17.9.930': '07.9.930',
        '17.9.932': '07.9.932',
        '17.9.933': '07.9.933',
        '17.9.934': '07.9.934',
        '17.9.935': '07.9.935',
        '18.0.101': '',
        '18.0.102': '',
        '18.0.103': '',
        '18.0.104': '',
        '18.0.105': '',
        '22.0.301': '05.0.301',
        '22.1.201': '18.1.201',
        '22.1.202': '18.1.202',
        '22.1.203': '18.1.203',
        '22.1.204': '18.1.204',
        '22.1.205': '18.1.205',
        '24.0.003': '',
        '24.0.004': '',
        '24.0.005': '',
        '24.0.007': '',
        '24.0.009': '',
        '24.0.017': '',
        '24.0.019': '',
        '24.0.204': '',
        '24.0.941': '07.9.941',
        '24.0.942': '07.9.942',
        '24.0.943': '07.9.943',
        '24.0.944': '07.9.944',
        '24.0.945': '07.9.945',
        '24.0.946': '07.9.946',
        '24.0.947': '07.9.947',
        '24.0.948': '07.9.948',
        '24.0.949': '07.9.949',
        '24.0.951': '07.9.951',
        '24.0.952': '07.9.952',
        '24.0.954': '07.9.954',
        '25.3.301': '14.0.301',
        '25.3.302': '14.0.302',
        '25.3.303': '14.0.303',
        '26.2.201': '',
        '26.2.202': '',
        '28.3.981': '07.9.981',
        '28.3.982': '07.9.982',
        '28.3.983': '07.9.983',
        '28.3.984': '07.9.984',
        '28.3.985': '07.9.985',
    }

    f = open(argv[2], 'rb')
    with transaction.manager:
        for line in f:
            parts = line.strip().split(None, 14)
            #0 ?
            #1 ?
            #2 country/region code
            #3 place id
            #4 latitude degrees (implicit North)
            #5 latitude minutes
            #6 longitude degrees
            #7 longitude minutes
            #8 language group
            #9 ?
            #10 id
            #11 longitude OUEST/EST
            #12 ?
            #13 ?
            #14 name
            if len(parts) == 14:
                parts.append('no name given')
            elif len(parts) != 15:
                print 'invalid line:'
                print line
                continue                         
            pointcode = parts[2] + '.' + parts[3]
            if pointcode in aliases and aliases[pointcode]:
                print 'applying alias:', pointcode, '->', aliases[pointcode]
                pointcode = aliases[pointcode]
            place = DBSession.query(PlaceOfInquiry).filter(PlaceOfInquiry.pointcode_old == pointcode).first()
            if place is None:
                reg = parts[2][:2] + r'\..\.' + parts[3]
                places = DBSession.query(PlaceOfInquiry).filter(text('pointcode_old ~ :reg')).params(reg=reg).all()
                if len(places) == 1:
                    print 'applying auto alias', pointcode, '->', places[0].pointcode_old
                    place = places[0]
                else:
                    places = DBSession.query(PlaceOfInquiry).filter(text('upper(name) = :name'))\
                      .params(name=parts[14]).all()
                    if len(places) == 1:
                        print 'applying auto alias from name', pointcode, '->', places[0].pointcode_old
                        place = places[0]
                    else:
                        print 'autoalias failed for', pointcode
                        continue
            lat = float(parts[4]) + float(parts[5])/60
            lng = float(parts[6]) + float(parts[7])/60
            if parts[11] == 'OUEST':
                lng = -lng
            elif parts[11] != 'EST':
                print 'invalid data', parts[11]

            candidates = DBSession.query(PlaceCandidate).filter(PlaceCandidate.place_of_inquiry_fkey == place.id).all()
            if len(candidates) == 0:
                print 'Found no candidates for', pointcode
            delta = [(diff(lat, lng, c.lat, c.lng), c) for c in candidates]
            delta.sort()
            neighbors = [d for d in delta if d[0] < 0.4]
            min_distance = delta[0][0] if delta else 0
            print '%i/%i %.4f %s "%s" "%s"' % (len(neighbors), len(candidates), min_distance,
                                            pointcode, place.name.encode('utf8'), parts[14])
            c = PlaceCandidate()
            c.place_of_inquiry_fkey = place.id
            c.name = parts[14]
            c.lat = lat
            c.lng = lng
            c.source = CandidateSource.ale
            DBSession.add(c)
            if neighbors:
                if not (place.lat and place.lng):
                    place.lat = neighbors[0][1].lat
                    place.lng = neighbors[0][1].lng
                if len(candidates) == 1:
                    place.coordinates_validated = True


if __name__ == '__main__':
    main()
