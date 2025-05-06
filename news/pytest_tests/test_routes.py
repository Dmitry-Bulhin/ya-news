import pytest
from http import HTTPStatus

from django.urls import reverse


@pytest.mark.parametrize(
    'url_fixture',
    (
        'home_url',
        'login_url',
        'logout_url',
        'signup_url'
    )
)
def test_public_pages_availability_for_anonymous_user(client, url_fixture, request):
    url = request.getfixturevalue(url_fixture)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_news_detail_availability_for_anonymous(client, news, detail_url):
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("url_fixture", (
    "comment_edit_url",
    "comment_delete_url",
))
def test_comment_routes_for_author(url_fixture, author_client, request):
    url = request.getfixturevalue(url_fixture)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize("url_fixture", (
    "comment_edit_url",
    "comment_delete_url",
))
def test_comment_routes_for_not_author(url_fixture, not_author_client, request):
    url = request.getfixturevalue(url_fixture)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.parametrize("url_fixture", (
    "comment_edit_url",
    "comment_delete_url",
))
def test_comment_routes_for_anonymous(url_fixture, anonymous_client, request):
    url = request.getfixturevalue(url_fixture)
    response = anonymous_client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert "/login/" in response.url


@pytest.mark.parametrize(
        'url_fixture',
        ('comment_edit_url', 'comment_delete_url')
    )
def test_comment_edit_delete_redirect_for_anonymous(
        client,
        login_url,
        url_fixture,
        request
    ):
    url = request.getfixturevalue(url_fixture)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_comment_edit_delete_for_other_user(not_author_client, comment, name):
    url = reverse(name, kwargs={'pk': comment.pk})
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND