import json

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    User,
    Concept,
    PlaceOfInquiry,
    PlaceCandidate,
    Scan,
    SheetEntry,
    SheetEntryState,
    )

from pyramid.httpexceptions import (
    HTTPMovedPermanently,
    HTTPFound,
    HTTPNotFound,
    HTTPUnauthorized,
    )

from pyramid.security import (
    authenticated_userid,
    remember,
    forget,
    )


@view_config(route_name='home', renderer='templates/overview.mako')
def main_view(request):
    username = authenticated_userid(request)
    return dict(username=username,
                overview=Concept.get_overview())


@view_config(route_name='register', renderer='templates/register.mako')
def register_view(request):
    username = authenticated_userid(request)
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
            if login_name == '':
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
    return dict(username=username,
                login_name=login_name,
                email = email,
                success_msg = success_msg,
                error_msg = error_msg,
                url_next = request.route_url('home'))


@view_config(route_name='login', renderer='templates/login.mako')
def login_view(request):
    username = authenticated_userid(request)
    url_next = request.params.get('next') or request.route_url('home')
    login_name = ''
    did_fail = False
    if 'submit' in request.POST:
        login_name = request.POST.get('login_name', '')
        password = request.POST.get('password', '')
        if User.check_password(login_name, password):
            headers = remember(request, login_name)
            username = authenticated_userid(request)
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
    username = authenticated_userid(request)
    concept_id = request.matchdict['concept_id']
    concept = Concept.get_by_id(concept_id)
    if concept is None:
        return HTTPNotFound()
    sheetEntries = SheetEntry.get_scan_entry_by_concept_id(concept_id)
    return dict(username=username,
                concept=concept,
                sheetEntries=sheetEntries)


@view_config(route_name='sheet', renderer='templates/sheet.mako')
def sheet_view(request):
    username = authenticated_userid(request)
    concept_id = request.matchdict['concept_id']
    scan_name = request.matchdict['scan_name']
    message = ''
    scan = Scan.get_by_concept_name(concept_id, scan_name)
    if scan is None:
        return HTTPNotFound()
    sheetEntry = SheetEntry.get_by_scan_id(scan.id)
    if 'submit' in request.POST:
        user = User.get_by_username(username)
        if user is None:
            return HTTPUnauthorized("Please log in to save changes.")
        if sheetEntry is None:
            sheetEntry = SheetEntry(scan.concept_fkey, scan.scan_name, scan.id, '')
            DBSession.add(sheetEntry)
        new_status = request.POST.get('status', '')
        if new_status not in SheetEntryState:
            return HTTPBadRequest("Invalid status code")
        sheetEntry.status = new_status
        sheetEntry.editor_fkey = user.id
        sheetEntry.data = request.POST.get('data', '')
        sheetEntry.comment = request.POST.get('comment', '')
        message = 'Sheet saved.'
    return dict(username=username,
                message=message,
                scan=scan,
                sheetEntry=sheetEntry,
                sheetEntryState=SheetEntryState)


@view_config(route_name='places', renderer='templates/places.mako')
def places_view(request):
    username = authenticated_userid(request)
    places = PlaceOfInquiry.get_overview()
    return dict(places=places, username=username)


@view_config(route_name='place_candidates', renderer='json')
def place_candidates_view(request):
    place_id = request.matchdict['place_id']
    try:
        place_id = int(place_id)
    except ValueError:
        request.response.status_code = 400
        return dict(status='INVALID_ARGUMENT', response=[])
    place = PlaceOfInquiry.get(place_id)
    place_json = dict(id=place.id, name=place.name, country_code=place.pointcode_new[2:], lat=place.lat, lng=place.lng)
    wanted = set(['id', 'name', 'country_code', 'lat', 'lng', 'feature_code', 'source', 'complete_data'])
    candidates = [{key: x.__dict__[key] for key in x.__dict__.keys() if key in wanted}
                   for x in PlaceCandidate.get_candidates(place_id) if x.lat != place.lat or x.lng != place.lng ]
    return dict(status='OK', selected=place_json, response=candidates)


@view_config(route_name='place_edit', renderer='json')
def place_edit(request):
    username = authenticated_userid(request)
    user = User.get_by_username(username)
    if user is None:
        request.response.status_code = 401
        return dict(status=401)
    try:
        place_id = int(request.matchdict['place_id'])
    except ValueError:
        request.response.status_code = 404
        return dict(status=404)
    place = PlaceOfInquiry.get(place_id)
    if request.method == 'POST':
        for key, k_type in [('name', unicode), ('lng', float), ('lat', float), ('remarks', unicode)]:
            value = request.POST.get(key, '').strip()
            if not value:
                continue
            try:
                value = k_type(value)
            except:
                request.response.status_code = 400
                return dict(status=400, reason='"%s" not of expected type "%s"' % (key, k_type.__name__))
            setattr(place, key, value)
        return dict(status='OK')
    else:
        request.response.status_code = 400
        return dict(status=400, reason='Unsupported HTTP method')
