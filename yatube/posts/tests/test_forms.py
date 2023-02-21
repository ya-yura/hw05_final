from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from ..forms import PostForm


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
        )
        cls.form = PostForm()

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.REVERSE_ADDRESS_PROFILE = reverse(
            'posts:profile', args=(self.author.username,)
        )
        self.REVERSE_ADDRESS_CREATE = reverse(
            'posts:post_create'
        )
        self.REVERSE_ADDRESS_EDIT = reverse(
            'posts:post_edit', args=(self.post.pk,)
        )
        self.REVERSE_ADDRESS_DETAIL = reverse(
            'posts:post_detail', args=(self.post.pk,)
        )

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        Post.objects.all().delete()
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostFormTests.group.id,
        }
        response = self.author_client.post(
            self.REVERSE_ADDRESS_CREATE,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, self.REVERSE_ADDRESS_PROFILE)
        self.assertEqual(
            Post.objects.count(),
            post_count + 1
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group,
            ).exists()
        )
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group.id, form_data['group'])

    def test_post_edit(self):
        """Проверяем, что происходит изменение поста."""
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        new_group = Group.objects.create(
            title='Тестовый измененный заголовок',
            slug='test-slug-fixed',
            description='Тестовое измененное описание',
        )
        form_data = {
            'text': 'Тестовый измененный текст',
            'group': new_group.id,
        }
        response = self.author_client.post(
            self.REVERSE_ADDRESS_EDIT,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, self.REVERSE_ADDRESS_DETAIL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(Post.objects.count(), 1)
        response = self.author_client.get(
            reverse(
                'posts:group_list',
                args=(self.group.slug,)
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(response.context.get('page_obj')), 0
        )

    def test_client_do_not_create_post(self):
        """Проверяем, что аноним не может создать пост."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.client.post(
            self.REVERSE_ADDRESS_CREATE,
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse(
            'users:login'
        ) + '?next=' + self.REVERSE_ADDRESS_CREATE
        self.assertRedirects(response, redirect)
        self.assertEqual(
            Post.objects.count(),
            post_count,
        )
