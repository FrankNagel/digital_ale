#!/usr/bin/env python

import re

from sqlalchemy import and_

from .models import (
    DBSession,
    Scan,
    SheetEntry,
    SheetEntryState,
    )

FILENAME_REGEX = re.compile(r'ALE QI-([0-9]{3}) ([0-9.a-z]+)\.txt', re.IGNORECASE)


def import_txt(filename, fileobj, user, parser=None):
    my_msg = []

    match = FILENAME_REGEX.search(filename)
    if not match:
        my_msg.append('Error: Couldn\'t determine concept Id and scan name from filename.')
        return my_msg
    concept_id = int(match.group(1))
    scan_name = match.group(2)

    scan = DBSession.query(Scan).filter(and_(Scan.concept_fkey == concept_id, Scan.scan_name == scan_name)).first()
    if scan is None:
        my_msg.append('Error: Scan does not exist.')
        return my_msg
    content = fileobj.read()
    if content.startswith('\xef\xbb\xbf'): #BOM
        content = content[3:]
    try:
        content = unicode(content, 'utf8')
    except UnicodeDecodeError:
        my_msg.append("Warning: File has Unicode errors.")
        content = unicode(content, 'utf8', errors='replace')
        content = content.replace(u'\uFFFD', u'@')
    entry = DBSession.query(SheetEntry).filter(SheetEntry.scan_fkey == scan.id).first()
    if entry is None:
        entry = SheetEntry(concept_id, scan.scan_name, scan.id, content)
        entry.editor_fkey = user.id
        if content.find('@') != -1:
            entry.status = SheetEntryState.contains_at
        else:
            entry.status = SheetEntryState.unchecked
        DBSession.add(entry)
        my_msg.append('Adding Entry.')
    else:
        my_msg.append('Warning: Overwriting existing entry.')
        entry.set_data(content)
        entry.editor_fkey = user.id

    if parser is not None:
        entry.extract_data(parser)
    return my_msg
