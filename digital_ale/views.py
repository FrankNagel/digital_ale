#!/usr/bin/env python

import traceback

import logging
log = logging.getLogger(__name__)

from zipfile import ZipFile

from pyramid.response import Response

from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    User,
    CandidateSource,
    Concept,
    PlaceOfInquiry,
    PlaceCandidate,
    Pronounciation,
    Role,
    Scan,
    SheetEntry,
    SheetEntryState,
    )

from pyramid.httpexceptions import (
    HTTPMovedPermanently,
    HTTPFound,
    HTTPNotFound,
    HTTPUnauthorized,
    HTTPForbidden,
    HTTPBadRequest
    )

from pyramid.security import (
    remember,
    forget,
    )

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from data_import import import_txt
from sheet_parser import SheetParser


@view_config(route_name='home', renderer='templates/overview.mako')
def main_view(request):
    username = request.authenticated_userid
    return dict(username=username,
                overview=Concept.get_overview())


@view_config(route_name='register', renderer='templates/register.mako')
def register_view(request):
    username = request.authenticated_userid
    login_name = ''
    email = ''
    success_msg = ''
    error_msg = ''

    if 'submit' in request.POST:
        login_name = request.POST.get('login_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        for _ in [None]:
            if login_name == '' or login_name.startswith('role:'):
                error_msg = 'Login name invalid.'
                break
            user = User.get_by_username(login_name)
            if user != None:
                error_msg = 'Login name already in use.'
                break
            if password == '':
                error_msg = 'Password must not be empty'
                break
            if password != confirm_password:
                error_msg = "Passwords don't match"
                break
            user = User(login_name, password, login_name, email)
            DBSession.add(user)
            success_msg = 'User created. You can log in now.'

            #send an email for newly registered user
            recipient = request.registry.settings.get('mail.address', None)
            if recipient:
                message = Message(subject="Digital ALE registration",
                                  sender="noreply@ale.paralleltext.info",
                                  recipients=[request.registry.settings['mail.address']],
                                  body="A New User registered:\n\t%s\n\t%s" % (login_name, email))
                mailer = get_mailer(request)
                mailer.send(message)
    return dict(username=username,
                login_name=login_name,
                email=email,
                success_msg=success_msg,
                error_msg=error_msg,
                url_next=request.route_url('home'))


@view_config(route_name='login', renderer='templates/login.mako')
def login_view(request):
    username = request.authenticated_userid
    url_next = request.params.get('next') or request.route_url('home')
    login_name = ''
    did_fail = False
    if 'submit' in request.POST:
        login_name = request.POST.get('login_name', '')
        password = request.POST.get('password', '')
        if User.check_password(login_name, password):
            headers = remember(request, login_name)
            username = request.authenticated_userid
            return HTTPFound(location=url_next, headers=headers)
        else:
            did_fail = True
    return {
        'username': username,
        'login_name': login_name,
        'url_next': url_next,
        'failed_attempt': did_fail,
    }


@view_config(route_name='logout', renderer='templates/login.mako')
def logout_view(request):
    request.session.invalidate()
    headers = forget(request)
    loc = request.route_url('home')
    return HTTPFound(location=loc, headers=headers)


@view_config(route_name='concept', renderer='templates/concept.mako')
def concept_view(request):
    username = request.authenticated_userid
    concept_id = request.matchdict['concept_id']
    concept = Concept.get_by_id(concept_id)
    if concept is None:
        return HTTPNotFound()
    sheetEntries = SheetEntry.get_scan_entry_by_concept_id(concept_id)
    return dict(username=username,
                concept=concept,
                sheetEntries=sheetEntries)


@view_config(route_name='concept_data', renderer='templates/concept_data.mako')
def concept_data_view(request):
    username = request.authenticated_userid
    concept_id = request.matchdict['concept_id']
    concept = Concept.get_by_id(concept_id)
    if concept is None:
        return HTTPNotFound()
    scans_sheets = SheetEntry.get_scan_entry_by_concept_id(concept_id)
    if 'recompute' in request.POST:
        places = DBSession.query(PlaceOfInquiry).all()
        parser = SheetParser(places)
        for _, sheetEntry in scans_sheets:
            if sheetEntry:
                sheetEntry.extract_data(parser)
        return HTTPFound(request.url)
    pronounciations = Pronounciation.get_by_concept_id(concept_id)
    have_messages = True
    return dict(username=username, concept=concept, scans_sheets=scans_sheets, pronounciations=pronounciations,
                have_messages=have_messages)

@view_config(route_name='sheet_prefix', renderer='templates/sheet_by_prefix.mako')
def sheet_prefix_view(request):
    username = request.authenticated_userid
    sheet_prefix = request.matchdict['sheet_prefix']
    scans_sheets = SheetEntry.get_scan_entry_by_prefix(sheet_prefix)
    if not scans_sheets:
        return HTTPNotFound()
    return dict(username=username, scans_sheets=scans_sheets, sheet_prefix=sheet_prefix)

@view_config(route_name='sheet_prefix_data', renderer='templates/concept_data.mako')
def sheet_prefix_data_view(request):
    username = request.authenticated_userid
    sheet_prefix = request.matchdict['sheet_prefix']
    scans_sheets = SheetEntry.get_scan_entry_by_prefix(sheet_prefix)
    if not scans_sheets:
        return HTTPNotFound()
    if 'recompute' in request.POST:
        places = DBSession.query(PlaceOfInquiry).all()
        parser = SheetParser(places)
        for _, sheetEntry in scans_sheets:
            if sheetEntry:
                sheetEntry.extract_data(parser)
        return HTTPFound(request.url)
    pronounciations = Pronounciation.get_by_scan_prefix(sheet_prefix)
    have_messages = True
    return dict(username=username, scans_sheets=scans_sheets, pronounciations=pronounciations,
                have_messages=have_messages)


@view_config(route_name='concept_tsv', renderer='string')
def concept_tsv_view(request):
    concept_id = request.matchdict['concept_id']
    concept = Concept.get_by_id(concept_id)
    if concept is None:
        return HTTPNotFound()
    terse = request.params.has_key('terse') and request.params.get('terse').lower() in ['yes', 'true', '1']
    pronounciations = Pronounciation.get_by_concept_id(concept_id)
    result = []
    for p, sheet_entry, scan in pronounciations:
        if terse:
            result.append('%s\t%s\t%s\t%s\n' % (p.pronounciation,
                                                ','.join(place.pointcode_old for place in p.observations),
                                                concept_id, sheet_entry.id))
        else:
            for place in p.observations:
                result.append('%s\t%s\t%s\t%s\n' % (p.pronounciation, place.pointcode_old, concept_id, sheet_entry.id))
    return ''.join(result)


@view_config(route_name='sheet', renderer='templates/sheet.mako')
def sheet_view(request):
    username = request.authenticated_userid
    concept_id = request.matchdict['concept_id']
    scan_name = request.matchdict['scan_name']
    scan = Scan.get_by_concept_name(concept_id, scan_name)
    if scan is None:
        return HTTPNotFound()
    sheetEntry = SheetEntry.get_by_scan_id(scan.id) # may be None
    return dict(username=username,
                scan=scan,
                sheetEntry=sheetEntry,
                sheetEntryState=SheetEntryState)


@view_config(route_name='places', renderer='templates/places.mako')
def places_view(request):
    username = request.authenticated_userid
    places = PlaceOfInquiry.get_overview()
    return dict(places=places, username=username)


@view_config(route_name='places_all', renderer='templates/places_all.mako')
def places_all_view(request):
    username = request.authenticated_userid
    return dict(username=username)


@view_config(route_name='place_candidates', renderer='json')
def place_candidates_view(request):
    place_id = request.matchdict['place_id']
    try:
        place_id = int(place_id)
    except ValueError:
        request.response.status_code = 400
        return dict(status='INVALID_ARGUMENT', response=[])
    place = PlaceOfInquiry.get(place_id)
    if place is None:
        request.response.status_code = 404
        return dict(status=404)
    wanted = set(['id', 'name', 'country_code', 'lat', 'lng', 'feature_code', 'source', 'complete_data'])
    candidates = [{key: x.__dict__[key] for key in x.__dict__.keys() if key in wanted}
                  for x in PlaceCandidate.get_candidates_for_place(place_id)]
    for c in candidates:
        c['selected'] = c['lat'] == place.lat and c['lng'] == place.lng
    return dict(status='OK', candidates=candidates)


coord_parser = lambda x: x and float(x) or None
coord_parser.__name__ = '<float>|null'

bool_parser = lambda x: True if x == 'true' else False
bool_parser.__name__ = 'true|false'

@view_config(route_name='place_edit', renderer='json', request_method='POST', permission='edit_place')
def place_edit(request):
    username = request.authenticated_userid
    user = User.get_by_username(username)
    if user is None:
        #should never happen
        raise HTTPForbidden()
    try:
        place_id = int(request.matchdict['place_id'])
    except ValueError:
        request.response.status_code = 404
        return dict(status=404)
    place = PlaceOfInquiry.get(place_id)
    place.coordinates_validated = True
    for key, k_type in [('name', unicode), ('lng', coord_parser), ('lat', coord_parser), ('remarks', unicode),
                        ('coordinates_validated', bool_parser)]:
        if not request.POST.has_key(key):
            continue
        value = request.POST.get(key).strip()
        try:
            value = k_type(value)
        except:
            request.response.status_code = 400
            return dict(status=400, reason='"%s" not of expected type "%s"' % (key, k_type.__name__))
        setattr(place, key, value)
    if place.lat == None or place.lng == None:
        place.lat = place.lng = None
        place.coordinates_validated = False
    return dict(status='OK')


@view_config(route_name='place_get', renderer='json', request_method='GET')
def place_get(request):
    try:
        place_id = int(request.matchdict['place_id'])
    except ValueError:
        request.response.status_code = 400
        return dict(status=400)
    place = PlaceOfInquiry.get(place_id)
    if not place:
        request.response.status_code = 404
        return dict(status=404)
    candidate_count = PlaceCandidate.get_candidates_count(place_id)
    wanted = set(['id', 'pointcode_old', 'pointcode_new', 'name', 'lat', 'lng', 'remarks', 'coordinates_validated'])
    response = {key: place.__dict__[key] for key in place.__dict__.keys() if key in wanted}
    response['candidate_count'] = candidate_count
    return response


@view_config(route_name='place_get_all', renderer='json', request_method='GET')
def place_get_all(request):
    places = DBSession.query(PlaceOfInquiry).filter('lat is not null').all()
    wanted = set(['id', 'pointcode_old', 'pointcode_new', 'name', 'lat', 'lng', 'remarks', 'coordinates_validated'])
    response = [{key: place.__dict__[key] for key in place.__dict__.keys() if key in wanted} for place in places]
    return dict(status='OK', places=response)


@view_config(route_name='place_candidate_add', renderer='json', request_method='POST', permission='edit_place')
def place_candidate_add(request):
    username = request.authenticated_userid
    user = User.get_by_username(username)
    if user is None:
        #should never happen
        raise HTTPForbidden()
    candidate = PlaceCandidate()
    for key, k_type, attr_name in [('place_id', int, 'place_of_inquiry_fkey'),
                                   ('name', unicode, 'name'),
                                   ('lat', float, 'lat'),
                                   ('lng', float, 'lng')]:
        value = request.POST.get(key, '').strip()
        if not value:
            continue
        try:
            value = k_type(value)
        except:
            request.response.status_code = 400
            return dict(status=400, reason='"%s" not of expected type "%s"' % (key, k_type.__name__))
        setattr(candidate, attr_name, value)
    if not (candidate.place_of_inquiry_fkey and candidate.lat and candidate.lng):
        request.response.status_code = 400
        return dict(status=400, reason='One of the neccessary attributes place_id, lat, lng is missing.')
    candidate.source = CandidateSource.manual
    DBSession.add(candidate)
    return dict(status='OK')


@view_config(route_name='place_candidate', renderer='json', request_method='DELETE', permission='edit_place')
def place_candidate_delete(request):
    username = request.authenticated_userid
    user = User.get_by_username(username)
    if user is None:
        #should never happen
        raise HTTPForbidden()
    try:
        candidate_id = int(request.matchdict['candidate_id'])
    except ValueError:
        request.response.status_code = 404
        return dict(status=404)
    candidate = PlaceCandidate.get_candidate(candidate_id)
    if not candidate:
        request.response.status_code = 404
        return dict(status=404, reason='Resource does not exist.')
    DBSession.delete(candidate)
    place = PlaceOfInquiry.get(candidate.place_of_inquiry_fkey)
    if place.lat == candidate.lat and place.lng == candidate.lng:
        place.lat = place.lng = None
        place.coordinates_validated = False
    return dict(status='OK')


@view_config(route_name='sheet_edit', renderer='json', request_method='POST', permission='edit_sheet')
def sheet_edit(request):
    username = request.authenticated_userid
    user = User.get_by_username(username)
    if user is None:
        #should never happen with active authorization policy
        raise HTTPForbidden()
    concept_id = request.matchdict['concept_id']
    scan_name = request.matchdict['scan_name']
    message = ''
    scan = Scan.get_by_concept_name(concept_id, scan_name)
    if scan is None:
        request.response.status_code = 404
        return dict(status=404)
    sheetEntry = SheetEntry.get_by_scan_id(scan.id)
    if sheetEntry is None:
        sheetEntry = SheetEntry(scan.concept_fkey, scan.scan_name, scan.id, '')
        DBSession.add(sheetEntry)

    new_status = request.POST.get('status', '')
    if new_status not in SheetEntryState:
        request.response.status_code = 400
        return dict(status=400, reason="Invalid status code")
    sheetEntry.status = new_status
    sheetEntry.editor_fkey = user.id
    sheetEntry.data = request.POST.get('data', '')
    sheetEntry.comment = request.POST.get('comment', '')
    try:
        sheetEntry.extract_data()
    except Exception:
        log.error(traceback.format_exc())
    return dict(status='OK')


@view_config(route_name='extract_pronounciation', renderer='json', request_method='POST', permission='bulk_extract')
def extract_pronounciation(request):
    sheets = SheetEntry.extract_pronounciation(request.POST.get('all', '').lower() in ('true', 'yes', '1'))
    return dict(status='OK', num_sheets=len(sheets))


@view_config(context=HTTPForbidden, route_name='place_edit', renderer='json', request_method='POST')
@view_config(context=HTTPForbidden, route_name='place_candidate_add', renderer='json', request_method='POST')
@view_config(context=HTTPForbidden, route_name='place_candidate', renderer='json', request_method='DELETE')
@view_config(context=HTTPForbidden, route_name='extract_pronounciation', renderer='json', request_method='POST')
@view_config(context=HTTPForbidden, route_name='sheet_edit', renderer='json', request_method='POST')
def json_authorization_error(request):
    username = request.authenticated_userid
    if username is None:
        request.response.status_code = 401
        return dict(status=401)
    else:
        request.response.status_code = 403
        return dict(status=403)


@view_config(route_name='admin_import_sheet', renderer='templates/admin_import_sheet.mako', request_method='GET',
             permission='admin')
def admin_import_sheet(request):
    return dict()


@view_config(route_name='admin_import_sheet', renderer='templates/admin_import_sheet.mako', request_method='POST',
             permission='admin')
def admin_import_sheet_post(request):
    sheet = request.POST.get('sheet', None)
    if sheet is None:
        raise HTTPBadRequest()
    user = User.get_by_username(request.authenticated_userid)
    if user is None:
        raise HTTPForbidden()
    import_msg = []
    places = DBSession.query(PlaceOfInquiry).all()
    parser = SheetParser(places)
    if sheet.filename.lower().endswith('.zip'):
        with ZipFile(sheet.file) as zip_file:
            for zip_info in zip_file.infolist():
                with zip_file.open(zip_info) as sheet_file:
                    msg = import_txt(zip_info.filename, sheet_file, user, parser)
                    import_msg.append((zip_info.filename, msg))
    else:
        msg = import_txt(sheet.filename, sheet.file, parser)
        import_msg.append((sheet.filename, msg))
    pre = []
    for filename, msg in import_msg:
        pre.append(filename)
        for m in msg:
            pre.append('\t' + m)
    pre = '\n'.join(pre)
    return dict(import_msg=pre)



@view_config(route_name='admin_users', renderer='templates/admin_users.mako', request_method='GET',
             permission='admin')
def admin_users(request):
    return dict(
        username=request.authenticated_userid,
        user_list=User.get_all_usernames()
    )


@view_config(route_name='admin_user_settings', renderer='templates/admin_user_settings.mako', request_method='GET',
             permission='admin')
def admin_user_settings(request):
    user = User.get_by_username(request.matchdict['user_id'])
    if user is None:
        raise HTTPNotFound()
    return dict(
        username=request.authenticated_userid,
        user=user,
        roles=list(Role)
        )


@view_config(route_name='admin_user_settings', renderer='templates/admin_user_settings.mako', request_method='POST',
             permission='admin')
def admin_user_settings_post(request):
    user = User.get_by_username(request.matchdict['user_id'])
    if user is None:
        raise HTTPNotFound()
    action = request.POST.get('action', '')
    if action == 'save_password':
        new_password = request.POST.get('password', '')
        user.password = new_password
    elif action == 'save_roles':
        new_roles = []
        for role in Role:
            if role in request.POST:
                new_roles.append(role)
        user.roles = new_roles
    return HTTPFound(request.url)
