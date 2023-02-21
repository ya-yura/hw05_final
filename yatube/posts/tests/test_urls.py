from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from django.contrib.auth import get_user_model


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый_заголовок',
            slug='test-slug',
            description='Тестовое_описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый_текст',
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user = User.objects.create_user(username='Has_no_Posts')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.name_args_templates = (
            ('posts:index', None, '/'),
            (
                'posts:group_list',
                (self.group.slug,),
                reverse('posts:group_list', kwargs={
                        'slug': self.group.slug}),
            ),
            (
                'posts:profile',
                (self.user,),
                reverse('posts:profile', kwargs={
                        'username': self.user}),
            ),
            (
                'posts:post_detail',
                (self.post.id,),
                reverse('posts:post_detail', kwargs={
                        'post_id': self.post.id}),
            ),
            (
                'posts:post_edit',
                (self.post.id,),
                reverse('posts:post_edit', kwargs={
                    'post_id': self.post.id}),
            ),
            ('posts:post_create', None, reverse('posts:post_create')),
        )

    def test_unexisting_page_has_not_found(self):
        """Страница '/unexisting_page/' не существует."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_all_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list', (self.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (self.user,), 'posts/profile.html'),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html'),
            ('posts:post_edit', (self.post.id,), 'posts/create_post.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
        )

        for name, args, template in templates:
            with self.subTest(name=name):
                response = self.author_client.get(reverse(name, args=args))
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, args, url in self.name_args_templates:
            with self.subTest(name=name, url=url):
                self.assertEqual(url, reverse(name, args=args))

    def test_all_url_available_author(self):
        """Все URL-адреса доступны автору."""
        for name, args, url in self.name_args_templates:
            with self.subTest(url=url):
                response = self.author_client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_all_url_available_not_author(self):
        """Все URL-адреса доступны НЕ автору."""
        for name, args, url in self.name_args_templates:
            with self.subTest(url=url):
                if name == 'post_edit':
                    response = self.authorized_client.get(
                        reverse(
                            'posts:post_edit',
                            args=(self.post.id,),
                        )
                    )
                    self.assertRedirects(response, reverse(
                        'posts:post_detail',
                        args=(self.post.id,),
                    ))

                    response = self.authorized_client.get(reverse(
                        name, args=args
                    ))

                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_all_url_available_guest(self):
        """Все URL-адреса доступны анониму."""
        for name, args, url in self.name_args_templates:
            login = reverse('users:login')
            reverse_name = reverse(name, args=args)
            if name == ['post_create', 'post_edit']:
                with self.subTest(url=url):
                    response = self.client.get(
                        reverse('posts:post_create'),
                        reverse('posts:post_edit', kwargs={
                                'post_id': self.post.id}),
                    )
                    self.assertRedirects(
                        response,
                        f'{login}?next={reverse_name}',
                    )
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_return_404(self):
        """Страница unexisting вернет 404."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
