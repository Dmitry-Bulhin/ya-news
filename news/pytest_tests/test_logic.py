import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus

from news.models import Comment
from news.forms import CommentForm, BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, news):
    comments_count = Comment.objects.count()
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data = {'text': 'Тестовый комментарий'}
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_count
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={url}'
    assert response.url == redirect_url


@pytest.mark.django_db
def test_authorized_user_can_post_comment(author_client, author, news):
    comments_count = Comment.objects.count()
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data = {'text': 'Тестовый комментарий'}
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_count + 1
    new_comment = Comment.objects.latest('id')
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.django_db
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_bad_words_not_published(author_client, news, bad_word):
    comments_count = Comment.objects.count()
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data = {'text': f'Текст содержит запрещенное слово {bad_word}'}
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == comments_count
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    new_text = 'Обновленный комментарий'
    form_data = {'text': new_text}
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    comments_count = Comment.objects.count()
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_count - 1


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_user_cant_edit_delete_others_comments(not_author_client, comment, url_name):
    url = reverse(url_name, kwargs={'pk': comment.pk})
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND