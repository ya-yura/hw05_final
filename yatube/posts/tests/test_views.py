from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post
from django.conf import settings

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'

        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

        cls.no_follow_user = User.objects.create_user(username='biba')
        cls.follow_user = User.objects.create_user(username='boba')
        cls.follower = Follow.objects.create(
            user=cls.follow_user, author=cls.user)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.follow_user)
        self.no_follower_client = Client()
        self.no_follower_client.force_login(self.no_follow_user)

    def context_test(self, response):
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author.username, self.user.username)
        self.assertEqual(post.group.slug, self.group.slug)
        self.assertEqual(post.image, self.post.image)

    def test_index_page_show_correct_context(self):
        """
        Шаблон index сформирован с правильным контекстом.
        Созданный пост появился на стартовой странице.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        self.context_test(response)

    def test_group_list_page_show_correct_context(self):
        """
        Шаблон group_list сформирован с правильным контекстом
        Созданный пост появился на странице группы
        """
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.context_test(response)

    def test_profile_page_show_correct_context(self):
        """
        Шаблон profile сформирован с правильным контекстом
        Созданный пост появился на странице профиля автора
        """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.context_test(response)

    def test_post_detail_page_show_correct_context(self):
        """
        Шаблон post_detail сформирован с правильным контекстом
        Подробная информация поста появляется на отдельной странице
        """
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        context_post = response.context.get('post')
        self.assertEqual(context_post.text, self.post.text)
        self.assertEqual(context_post.image, self.post.image)

    def test_index_cache1(self):
        """Тест кэша 1"""
        post = Post.objects.create(
            author=self.user,
            text='Новый тестовый пост'
        )
        response = self.authorized_client.get(reverse('posts:index'))
        temp = response.content
        post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, temp)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, temp)

    def test_index_cache2(self):
        """Тест кэша2"""
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.filter(pk=post.pk).delete()
        response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response2.content)

    def test_follow_index_show_cont(self):
        """Шаблон follow сформирован с правильным контекстом."""
        response = self.follower_client.get(reverse('posts:follow_index'))
        count_post_follower = len(response.context['page_obj'])
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        count_post_no_follower = len(response.context['page_obj'])
        Post.objects.create(
            author=self.user,
            text='Новый тестовый пост',
            group=self.group,
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj']), count_post_follower + 1)
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj']), count_post_no_follower)

    def test_user_follow(self):
        """Проверка на создание подписчика."""
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        count_post_follower = len(response.context['page_obj'])
        response = self.no_follower_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user}))
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        self.assertFalse(count_post_follower)
        self.assertTrue(len(response.context['page_obj']))

    def test_follower_delete_to_user(self):
        """Проверка на удаление подписчика."""
        response = self.follower_client.get(reverse('posts:follow_index'))
        count_post_follower = len(response.context['page_obj'])
        response = self.follower_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user}))
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertTrue(count_post_follower)
        self.assertFalse(len(response.context['page_obj']))


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.count_post = 13
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        for page_object in range(cls.count_post):
            Post.objects.create(
                text=f'Тестовый текст{page_object}',
                author=cls.user,
                group=cls.group
            )

    def test_two_page_paginators(self):
        """Корректная работа паджинатора на двух страницах."""
        paginators_list = (
            ('posts:posts_index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user.username,)),
        )
        for reverse_name, arg in paginators_list:
            with self.subTest(reverse_name=reverse_name):
                response_firs = self.client.get(
                    reverse(reverse_name, args=arg))
                response_second = self.client.get(
                    reverse(reverse_name, args=arg) + '?page=2')
                self.assertEqual(
                    len(response_firs.context['page_obj']
                        ), settings.COUNT_POST)
                self.assertEqual(
                    len(response_second.context['page_obj']
                        ), self.count_post - settings.COUNT_POST)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(username='user')
        cls.user_following = User.objects.create_user(username='user_1')
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Тестовый текст',
        )

    def setUp(self):
        self.following_client = Client()
        self.follower_client = Client()
        self.following_client.force_login(self.user_following)
        self.follower_client.force_login(self.user_follower)

    def test_follow(self):
        """Зарегистрированный пользователь может подписываться."""
        follower_count = Follow.objects.count()
        self.follower_client.get(reverse(
            'posts:profile_follow',
            args=(self.user_following.username,)))
        self.assertEqual(Follow.objects.count(), follower_count + 1)

    def test_unfollow(self):
        """Зарегистрированный пользователь может отписаться."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        follower_count = Follow.objects.count()
        self.follower_client.get(reverse(
            'posts:profile_unfollow',
            args=(self.user_following.username,)))
        self.assertEqual(Follow.objects.count(), follower_count - 1)

    def test_new_post_see_follower(self):
        """Пост появляется в ленте подписавшихся."""
        posts = Post.objects.create(
            text=self.post.text,
            author=self.user_following,
        )
        follow = Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post, posts)
        follow.delete()
        response_2 = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response_2.context['page_obj']), 0)
