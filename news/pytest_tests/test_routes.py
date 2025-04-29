import pytest
from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_public_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_availability_for_anonymous(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_edit_delete_availability_for_author(author_client, comment):
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, kwargs={'pk': comment.pk})
        response = author_client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_comment_edit_delete_redirect_for_anonymous(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, kwargs={'pk': comment.pk})
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_comment_edit_delete_for_other_user(not_author_client, comment, name):
    url = reverse(name, kwargs={'pk': comment.pk})
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND