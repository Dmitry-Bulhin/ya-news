from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

from news.models import News, Comment
from news.forms import CommentForm


def test_news_count_on_home_page(client, home_url):
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(11)
    )
    response = client.get(home_url)
    assert 'object_list' in response.context, (
        'Проверьте, что передали `object_list` в контекст шаблона.'
    )
    assert response.context['object_list'].count() == 10, (
        'На главной странице должно быть ровно 10 новостей'
    )


def test_news_order_on_home_page(client, home_url):
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        )
        for index in range(3)
    )
    response = client.get(home_url)
    assert 'object_list' in response.context, (
        'Проверьте, что передали `object_list` в контекст шаблона.'
    )
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


def test_comments_order_on_news_detail_page(client, news, detail_url):
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
    response = client.get(detail_url)
    assert 'news' in response.context, (
        'Проверьте, что передали объект `news` в контекст шаблона.'
    )
    news_from_context = response.context['news']
    comments = news_from_context.comment_set.all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times)


def test_anonymous_client_has_no_comment_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context, (
        'Проверьте, что не передаёте форму анонимным пользователям.'
    )


def test_authorized_client_has_comment_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context, (
        'Проверьте, что передаёте форму авторизованным пользователям.'
    )
    assert isinstance(response.context['form'], CommentForm), (
        'Проверьте, что форма в контексте — это `CommentForm`.'
    )