import pytest
from datetime import datetime, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model

from news.models import News, Comment
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_on_home_page(client):
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(11)
    )
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == 10


@pytest.mark.django_db
def test_news_order_on_home_page(client):
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        )
        for index in range(3)
    )
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order_on_news_detail_page(client, news):
    now = datetime.now()
    author = get_user_model().objects.create(username='Комментатор')
    Comment.objects.bulk_create(
        Comment(
            news=news,
            author=author,
            text=f'Комментарий {index}',
            created=now - timedelta(hours=index)
        )
        for index in range(3)
    )
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'news' in response.context
    comments = response.context['news'].comment_set.all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times)


@pytest.mark.django_db
def test_anonymous_client_has_no_comment_form(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_comment_form(author_client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)