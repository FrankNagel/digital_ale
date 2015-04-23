from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    RootFactory,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    session_factory = SignedCookieSessionFactory(
        settings['session.secret'],
        timeout = settings.get('session.timeout', 3600),
        reissue_time = settings.get('session.reissue_time', 360)
        )

    authn_policy = SessionAuthenticationPolicy()
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        root_factory=RootFactory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        session_factory=session_factory
        )

    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    config.add_route('home', '/')
    config.add_route('register', '/register')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('places', '/places')
    config.add_route('places_all', '/all_places')
    config.add_route('concept', '/q/{concept_id}')
    config.add_route('concept_data', '/q/{concept_id}/data')
    config.add_route('concept_tsv', '/q/{concept_id}/tsv')
    config.add_route('sheet_prefix', '/s/{sheet_prefix}')
    config.add_route('sheet_prefix_data', '/s/{sheet_prefix}/data')
    config.add_route('sheet', 'q/{concept_id}/{scan_name}')

    config.add_route('place_candidates', '/api/place_candidates/{place_id}')
    config.add_route('place_get_all', '/api/place/all')
    config.add_route('place_get', '/api/place/{place_id}')
    config.add_route('place_edit', '/api/place/{place_id}/edit')
    config.add_route('place_candidate_add', '/api/place_candidate/add')
    config.add_route('place_candidate', '/api/place_candidate/{candidate_id}')
    config.add_route('sheet_edit', '/api/sheet/{concept_id}/{scan_name}/edit')
    config.add_route('extract_pronounciation', '/api/extract')
    config.scan()
    return config.make_wsgi_app()
