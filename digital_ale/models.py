import os.path
from collections import namedtuple

from sqlalchemy import (
    Column,
    DDL,
    DefaultClause,
    and_,
    event,
    ForeignKey,
    Index,
    Integer,
    Text,
    text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    column_property,
    synonym,
    joinedload,
    )

from sqlalchemy.types import (
    Enum,
    Integer,
    Unicode,
    UnicodeText,
    DateTime,
    Enum,
    )

from pyramid.security import (
    Everyone,
    Authenticated,
    Allow,
    )

from zope.sqlalchemy import ZopeTransactionExtension

import cryptacular.bcrypt

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

def hash_password(password):
    return unicode(crypt.encode(password))


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    """
    Application's user model.
    """
    __tablename__ = 'tbl_user'
    id = Column(Integer, primary_key=True)
    login_name = Column(Unicode(50), unique=True)
    display_name = Column(Unicode(50))
    email = Column(Unicode(80))

    _password = Column('password', Unicode(60))

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    def __init__(self, login_name, password, display_name, email):
        self.login_name = login_name
        self.display_name = display_name
        self.email = email
        self.password = password

    @classmethod
    def get_by_username(cls, username):
        return DBSession.query(cls).filter(cls.login_name == username).first()

    @classmethod
    def check_password(cls, username, password):
        user = cls.get_by_username(username)
        if not user:
            return False
        return crypt.check(user.password, password)

    
class Scan(Base):
    __tablename__ = 'tbl_scan'
    id = Column(Integer, primary_key=True)
    concept_fkey = Column(Integer, ForeignKey('tbl_concept.id'))
    scan_name = Column(Unicode(256))
    uploader_fkey = Column(Integer, ForeignKey('tbl_user.id'))
    modification_date = Column(DateTime, DefaultClause(text('now()')))

    def get_path_to_file(self):
        return os.path.join('%03i' % self.concept_fkey,
                            'ale-qi-%03i-%s.jpg' % (self.concept_fkey, self.scan_name))

    def __init__(self, concept_fkey, scan_name):
        self.concept_fkey = concept_fkey
        self.scan_name = scan_name
        self.uploader_fkey = None
        self.modification_date = None

    @classmethod
    def get_by_concept_name(cls, concept_id, scan_name):
        return DBSession.query(Scan).filter(and_(Scan.concept_fkey == concept_id, Scan.scan_name == scan_name)).first()

SheetEntryStateClass = namedtuple('SheetEntryState', 'unchecked contains_at in_progress problematic ok ignore')
SheetEntryState = SheetEntryStateClass('Unchecked', 'Contains @', 'In Progress', 'Problematic', 'OK', 'Ignore')

class SheetEntry(Base):
    __tablename__ = 'tbl_sheet_entry'
    id = Column(Unicode(32), primary_key=True)
    scan_fkey = Column(Integer, ForeignKey('tbl_scan.id'), index=True)
    editor_fkey = Column(Integer, ForeignKey('tbl_user.id'))
    modification_date = Column(DateTime, DefaultClause(text('now()')))
    data = Column(Unicode())
    status = Column(Enum(*SheetEntryState, name='sheetEntryState'))
    comment = Column(Unicode())
    
    def __init__(self, concept_id, scan_name, scan_fkey, data):
        self.id = '%s-%s' % (concept_id, scan_name)
        self.scan_fkey = scan_fkey
        self.editor_fkey = None
        self.modification_date = None
        self.data = data

        self.comment = ''

    @classmethod
    def get_by_scan_id(cls, scan_id):
        return DBSession.query(SheetEntry).filter(SheetEntry.scan_fkey == scan_id).first()

    @classmethod
    def get_scan_entry_by_concept_id(cls, concept_id):
        return DBSession.query(Scan, SheetEntry).outerjoin(SheetEntry, Scan.id == SheetEntry.scan_fkey) \
          .filter(Scan.concept_fkey == concept_id) \
          .order_by(Scan.scan_name) \
          .all()


class SheetEntryHistory(Base):
    __tablename__ = 'tbl_sheet_entry_history'
    id = Column(Integer, primary_key=True)
    sheet_entry_fkey = Column(Unicode(32), ForeignKey('tbl_sheet_entry.id'))
    scan_fkey = Column(Integer, ForeignKey('tbl_scan.id'))
    editor_fkey = Column(Integer, ForeignKey('tbl_user.id'))
    modification_date = Column(DateTime)
    data = Column(Unicode())
    comment = Column(Unicode())


class Concept(Base):
    __tablename__ = 'tbl_concept'
    id = Column(Integer, primary_key=True)
    eng = Column(Unicode(128))
    fra = Column(Unicode(128))

    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).filter(cls.id == id).first()

    @classmethod
    def get_overview(cls):
        cmd = """\
select tc.id, tc.eng, tc.fra,
	count(ts.id) as num_scans, 
	count(te.status = 'Unchecked' or null) as num_unchecked,
	count(te.status = 'Contains @' or null) as num_contains_at,
	count(te.status = 'In Progress' or null) as num_in_progress,
	count(te.status = 'Problematic' or null) as num_problematic,
	count(te.status = 'OK' or null) as num_ok,
	count(te.status = 'Ignore' or null) as num_ignore,
	count(ts.id) - count(te.status) as num_missing
from tbl_concept tc
    left join tbl_scan ts on tc.id = ts.concept_fkey
	left join tbl_sheet_entry te on ts.id = te.scan_fkey
group by tc.id
order by tc.id"""
        result = DBSession.execute(cmd)
        Record = namedtuple('AleOverview', result.keys())
        return [Record(*r) for r in result.fetchall()]


class RootFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'post')
    ]

    def __init__(self, request):
        pass  # pragma: no cover
