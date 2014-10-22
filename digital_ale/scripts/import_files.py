#!/usr/bin/env python

import os, os.path
import shutil
import sys
import transaction
import datetime

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
    DBSession,
    Base,
    Scan,
    SheetEntry,
    SheetEntryState,
    User,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <filename>..\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

#WORK
def import_jpg(filename, dest_prefix, userid):
    basename = os.path.basename(filename)
    concept_id = basename[7:10]
    scan_name = basename[11:-4]
    dest_dir = os.path.join(dest_prefix, concept_id)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    elif not (os.path.isdir(dest_dir) and os.access(dest_dir, os.R_OK|os.W_OK|os.X_OK)):
        print >> sys.stderr, "Warning: Can't access destination directory '%s'" % dest_dir
        return
    scan = DBSession.query(Scan).filter(and_(Scan.concept_fkey == int(concept_id), Scan.scan_name == scan_name)).first()
    if scan == None:
        scan = Scan(int(concept_id), scan_name)
        scan.uploader_fkey = userid
        DBSession.add(scan)
        print >> sys.stderr, "Adding %s" % filename
    else:
        scan.modification_date = datetime.datetime.now()
        print >> sys.stderr, "Updating %s" % filename
    dest_path = os.path.normpath(os.path.join(dest_prefix, scan.get_path_to_file()))
    cwd = os.getcwd()
    source_path = os.path.normpath(os.path.join(cwd, filename))
    if dest_path != source_path:
        shutil.copy(source_path, dest_path)


#WORK
def import_txt(filename, userid):
    basename = unicode(os.path.basename(filename), 'utf8')
    concept_id = basename[7:10]
    scan_name = basename[11:-4]
    scan = DBSession.query(Scan).filter(and_(Scan.concept_fkey == concept_id, Scan.scan_name == scan_name)).first()
    if scan is None:
        print >> sys.stderr, "Warning: Scan does not exist for %s: Skipping" % filename
        return
    cwd = os.getcwd()
    fullpath = os.path.join(cwd, filename)
    if not (os.path.isfile(fullpath) and os.access(fullpath, os.R_OK)):
        print >> sys.stderr, "Warning: Can't access %s: Skipping" % filename
        return
    with file(fullpath) as f:
        content = f.read()
        if content.startswith('\xef\xbb\xbf'): #BOM
            content = content[3:]
        try:
            content = unicode(content, 'utf8')
        except UnicodeDecodeError, e:
            print >> sys.stderr, "Warning: '%s' doesn't parse as unicode; trying latin-9\n" %  filename, e
            try:
                content = unicode(content, 'latin9')
                print >> sys.stderr, "Notice: '%s' parsed as latin-9" % filename
            except UnicodeError, e:
                print >> sys.stderr, "Error: '%s' doesn't parse as neither unicode nor latin-9\n" %  filename, e
                return
    entry = DBSession.query(SheetEntry).filter(SheetEntry.scan_fkey == scan.id).first()
    if entry is None:
        entry = SheetEntry(concept_id, scan.scan_name, scan.id, content)
        entry.editor_fkey = userid
        if content.find('@') != -1:
            entry.status = SheetEntryState.contains_at
        else:
            entry.status = SheetEntryState.unchecked
        DBSession.add(entry)
        print >> sys.stderr, "Adding Entry for '%s'" % filename
    else:
        print >> sys.stderr, "Warning: Entry for '%s' already exists" % filename

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
    dest_prefix = resolver.resolve(settings['scans.prefix']).abspath()
    engine = engine_from_config(settings, 'sqlalchemy.')
    
    DBSession.configure(bind=engine)
    user = User.get_by_username(u'frank')
    userid = user and user.id or None
    #Base.metadata.create_all(engine)
    with transaction.manager:
        for filename in sys.argv[2:]:
            if filename[-3:] == 'jpg':
                import_jpg(filename, dest_prefix, userid)
            elif filename[-3:] == 'txt':
                import_txt(filename, userid)
            else:
                print >> sys.stderr, "Warning: (%s) Unknown filetype. Not importing.  " % filename

if __name__ == '__main__':
    main()
