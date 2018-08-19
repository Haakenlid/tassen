"""Core views for webpage."""

import json
import logging

import requests

from api.frontpage import FrontpageStoryViewset
from api.issues import IssueViewSet
from api.publicstories import PublicStoryViewSet
from api.site import SiteDataAPIView
from api.user import AvatarUserDetailsSerializer
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from utils.decorators import cache_memoize

logger = logging.getLogger(__name__)


def express_render(redux_actions, request):
    """Server side rendering of react app"""
    adapter = requests.adapters.HTTPAdapter(max_retries=8)
    session = requests.Session()
    session.mount(settings.EXPRESS_SERVER_URL, adapter)
    data = {'actions': redux_actions, 'url': request.build_absolute_uri()}
    path = request.path.replace('//', '/').lstrip('/')
    try:
        response = session.post(
            url=f'{settings.EXPRESS_SERVER_URL}/{path}',
            json=data,
            timeout=5,
        )
    except (requests.ConnectionError, request.Timeout) as e:
        logger.exception('Could not connect to express server')
        return {'state': {}, 'error': f'{e}'}
    try:
        return response.json()
    except json.JSONDecodeError as e:
        logger.exception('Invalid JSON from express')
        return {'state': {}, 'error': f'{e}\n{response.content}'}


def only_anon(request, *args):
    user_id = 0 if request.user.is_anonymous else request.user.pk
    return [user_id, *args]


@cache_memoize(timeout=60 * 60, args_rewrite=only_anon)
def fetch_user(request):
    if request.user.is_authenticated:
        serializer = AvatarUserDetailsSerializer(
            request.user, context={'request': request}
        )
        payload = json.loads(json.dumps(serializer.data))
        return {'type': 'auth/REQUEST_USER_SUCCESS', 'payload': payload}
    else:
        return {'type': 'auth/REQUEST_USER_FAILED'}


def fetch_story(request, pk):
    response = PublicStoryViewSet.as_view({'get': 'retrieve'})(request, pk=pk)
    payload = {
        **response.data,
        'HTTPstatus': response.status_code,
        'id': pk,
    }
    payload = json.loads(json.dumps(payload))
    return {'type': 'publicstory/STORY_FETCHED', 'payload': payload}


@cache_memoize(timeout=60, args_rewrite=only_anon)
def fetch_newsfeed(request):
    response = FrontpageStoryViewset.as_view({'get': 'list'})(request)
    return {'type': 'newsfeed/FEED_FETCHED', 'payload': response.data}


@cache_memoize(timeout=60 * 60, args_rewrite=only_anon)
def fetch_issues(request):
    response = IssueViewSet.as_view({'get': 'list'})(request)
    payload = {'issues': response.data.get('results')}
    return {'type': 'issues/ISSUES_FETCHED', 'payload': payload}


@cache_memoize(timeout=60 * 60, args_rewrite=only_anon)
def fetch_site(request):
    response = SiteDataAPIView.as_view()(request)
    return {'type': 'site/SITE_FETCHED', 'payload': response.data}


def get_redux_actions(request, story):
    """Redux actions to simulate data prefetching server side rendering."""
    actions = [
        fetch_newsfeed(request),
        fetch_site(request),
        fetch_issues(request),
        fetch_user(request),
    ]
    if story:
        actions.append(fetch_story(request, int(story)))
    return actions


def clear_cached_story(story):
    cache_key = f'cached_page_{story.pk}'
    cache.delete(cache_key)


def clear_cached_path(path):
    cache_key = f'cached_page_{path}'
    cache.delete(cache_key)


def react_frontpage_view(request, section=None, story=None, slug=None):

    cache_key = f'cached_page_{story or request.path}'

    if request.user.is_anonymous:
        response, path = cache.get(cache_key, (None, None))
        if response:
            if path != request.path:
                return redirect(path)
            logger.debug(f'{cache_key} {request}')
            return response

    redux_actions = get_redux_actions(request, story)
    ssr_context = express_render(redux_actions, request)

    try:
        pathname = ssr_context['state']['location']['pathname']
        if pathname != request.path:
            return redirect(pathname)
    except KeyError:
        pass

    status_code = ssr_context.pop('HTTPStatus', 200)
    if status_code == 404 and request.path[-1] != '/':
        return redirect(request.path + '/')

    response = render(
        request,
        template_name='universitas-server-side-render.html',
        context={'ssr': ssr_context},
        status=status_code,
    )

    if request.user.is_anonymous and status_code == 200:
        TEN_MINUTES = 60 * 10
        cache.set(cache_key, (response, request.path), TEN_MINUTES)

    return response


class TextTemplateView(TemplateView):
    """ Render plain text file. """

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'text/plain'
        return super().render_to_response(context, **response_kwargs)


class HumansTxtView(TextTemplateView):
    """ humans.txt contains information about who made the site. """

    template_name = 'humans.txt'


class RobotsTxtView(TextTemplateView):
    """ robots.txt contains instructions for webcrawler bots. """

    if settings.DEBUG:
        template_name = 'robots-staging.txt'
    else:
        template_name = 'robots-production.txt'
