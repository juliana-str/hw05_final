from http import HTTPStatus

from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from ..models import Comment, Group, Post, User, Follow

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тест описание'
USER_USERNAME = 'Anonimus'
USER_USERNAME1 = 'Vasya'
USER_USERNAME2 = 'Fedya'
POST_TEXT = 'Тестовая запись для тестового поста номер'
SECOND_PAGE_COUNT = 3


class Cache_pageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_client = Client()
        cls.user_author = User.objects.create_user(username=USER_USERNAME1)
        cls.authorized_client.force_login(cls.user_author)
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user_author,
        )
        cache.clear()

    def test_cache_page(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn(self.post, response.context['page_obj'])
        self.post.delete()
        self.assertFalse(Post.objects.filter(author=self.user_author).exists())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        Post.objects.bulk_create(
            [Post(text=POST_TEXT,
                  author=cls.user,
                  group=cls.group)
             for _ in range(settings.POST_COUNT + SECOND_PAGE_COUNT)]
        )
        cache.clear()

    def test_paginator(self):
        cache.clear()
        reverse_names = {
            reverse('posts:index'): settings.POST_COUNT,
            reverse('posts:index') + '?page=2': SECOND_PAGE_COUNT,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): settings.POST_COUNT,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})
            + '?page=2': SECOND_PAGE_COUNT,
            reverse('posts:profile',
                    kwargs={'username': self.user}): settings.POST_COUNT,
            reverse('posts:profile',
                    kwargs={'username': self.user})
            + '?page=2': SECOND_PAGE_COUNT,
        }
        for reverse_name, expected in reverse_names.items():
            with self.subTest(reverse_name=reverse_name, expected=expected):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 expected)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USER_USERNAME)
        cls.authorized_client = Client()
        cls.author = Client()
        cls.user_author = User.objects.create_user(username=USER_USERNAME1)
        cls.authorized_client.force_login(cls.user)
        cls.author.force_login(cls.user_author)
        cls.the_group = Group.objects.create(
            title=f'{GROUP_TITLE} 1',
            slug=f'{GROUP_SLUG}_1',
            description=GROUP_DESCRIPTION,
        )
        cls.other_group = Group.objects.create(
            title=f'{GROUP_TITLE} 2',
            slug=f'{GROUP_SLUG}_2',
            description=GROUP_DESCRIPTION,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user_author,
            group=cls.the_group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.post.author,
            text='Тестовый комментарий',
        )
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:group_list',
                    kwargs={'slug': self.the_group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'}

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_uses_correct_template(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        template = 'posts/index.html'
        self.assertTemplateUsed(response, template)

    def post_correct_context(self, response):
        first_object = response.context['page_obj'][0]
        post_group = first_object.group
        post_text = first_object.text
        post_pk = first_object.pk
        post_image = first_object.image
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_pk, self.post.pk)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_image, self.post.image)

    def test_correct_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.post_correct_context(response)
        self.assertIn(self.post, response.context['page_obj'])

    def test_group_post_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.the_group.slug})
        )
        self.post_correct_context(response)
        self.assertEqual(response.context.get('group'), self.the_group)
        self.assertIn(self.post, response.context['page_obj'])

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (
            self.author.get(reverse(
                'posts:profile',
                kwargs={'username': self.user_author})
            )
        )
        self.assertEqual(response.context.get('author'), self.user_author)
        self.assertIn(self.post, response.context['page_obj'])

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk})
        ))
        self.assertEqual(response.context['post'], self.post)

    def test_post_not_in_other_groups(self):
        """Пост только в нужной группе."""
        url = (reverse('posts:group_list',
                       kwargs={'slug': self.other_group.slug}))
        response = self.authorized_client.get(url)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.author.get(reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.pk})
        ))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('post'), self.post)
        self.assertEqual(response.context.get('is_edit'), True)

    def test_post_create_correct_redirect(self):
        response = self.client.get(
            reverse('posts:post_create'), follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect_url = (
            reverse('users:login') + '?next=' + reverse('posts:post_create')
        )
        self.assertRedirects(response, redirect_url)

    def test_post_edit_correct_redirect(self):
        response = self.client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect_url = (
            reverse('users:login') + '?next=' + reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        self.assertRedirects(response, redirect_url)

    def test_add_comment_correct_redirect_for_authorized_user(self):
        response = self.authorized_client.get(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect_url = (
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertRedirects(response, redirect_url)

    def test_add_comment_correct_redirect_for_guest(self):
        response = self.guest_client.get(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect_url = (
            reverse('users:login') + ('?next=%2Fposts%2F1%2Fcomment%2F')
        )
        self.assertRedirects(response, redirect_url)

    def test_comment_exist_on_post_detail(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertIn(self.comment, response.context['comments'])


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.non_follower = Client()
        cls.authorized_client = Client()
        cls.author = Client()
        cls.user = User.objects.create_user(username=USER_USERNAME)
        cls.author = User.objects.create_user(username=USER_USERNAME1)
        cls.n_follower = User.objects.create_user(username=USER_USERNAME2)
        cls.authorized_client.force_login(cls.user)
        cls.non_follower.force_login(cls.n_follower)
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
        )
        cls.follow = Follow.objects.create(
            author=cls.post.author,
            user=cls.user
        )

    def test_follow_index(self):
        response = self.authorized_client.get(reverse('posts:follow_index'))
        template = 'posts/follow.html'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, template)
        self.assertIn(self.post, response.context['page_obj'])

    def test_new_post_in_followers(self):
        """Пост в ленте только у подписчиков."""
        url = (reverse('posts:follow_index'))
        response = self.authorized_client.get(url)
        self.assertIn(self.post, response.context['page_obj'])

    def test_new_post_not_in_nonfollowers(self):
        """Пост не появляется в ленте тех, кто не подписан """
        url = (reverse('posts:follow_index'))
        response = self.non_follower.get(url)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_profile_follow(self):
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.author
        ).exists())

    def test_profile_unfollow(self):
        Follow.objects.filter(
            user=self.user, author=self.author
        ).delete()
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.author
        ).exists())
