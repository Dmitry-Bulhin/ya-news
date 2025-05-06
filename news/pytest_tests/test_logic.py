import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_anonymous_user_cant_post_comment(client, detail_url, login_url):
    comments_count = Comment.objects.count()
    form_data = {'text': 'Тестовый комментарий'}
    response = client.post(detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_count
    assertRedirects(
        response,
        f'{login_url}?next={detail_url}',
        status_code=HTTPStatus.FOUND,
        target_status_code=HTTPStatus.OK
    )


def test_authorized_user_can_post_comment(
        author_client,
        author, news,
        detail_url
    ):
    initial_count = Comment.objects.count()
    existing_ids = set(Comment.objects.values_list('id', flat=True))
    form_data = {'text': 'Тестовый комментарий'}
    response = author_client.post(detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count + 1
    new_comment = Comment.objects.exclude(id__in=existing_ids).get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_bad_words_not_published(
        author_client,
        bad_word,
        detail_url
    ):
    comments_count = Comment.objects.count()
    form_data = {'text': f'Текст содержит запрещенное слово {bad_word}'}
    response = author_client.post(detail_url, data=form_data)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == comments_count
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']


def test_author_can_edit_comment(author_client, comment, comment_edit_url):
    comments_count_before = Comment.objects.count()
    form_data = {'text': 'Обновленный комментарий'}
    response = author_client.post(comment_edit_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_count_before
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == form_data['text']
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author
    assert updated_comment.created == comment.created


def test_author_can_delete_comment(author_client, comment, comment_delete_url):
    comment_pk = comment.pk
    comments_count_before = Comment.objects.count()
    response = author_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before - 1
    assert not Comment.objects.filter(pk=comment_pk).exists()


def test_user_cant_edit_others_comments(
        not_author_client,
        comment,
        comment_edit_url
    ):
    original_text = comment.text
    comments_count_before = Comment.objects.count()
    form_data = {'text': 'Попытка изменить чужой комментарий'}
    response = not_author_client.post(comment_edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
    unchanged_comment = Comment.objects.get(pk=comment.pk)
    assert unchanged_comment.text == original_text


def test_user_cant_delete_others_comments(
        not_author_client,
        comment,
        comment_delete_url
    ):
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
    assert Comment.objects.filter(pk=comment.pk).exists()