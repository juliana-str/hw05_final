from http import HTTPStatus
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тест описание'
USER_USERNAME = 'Anonimus'
POST_TEXT = 'Тестовая запись для тестового поста номер'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USER_USERNAME)
        cls.authorised_client = Client()
        cls.authorised_client.force_login(cls.user)
        cls.the_group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.the_post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.the_group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает пост."""
        post_count = Post.objects.count()

        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'group': self.the_group.pk,
            'text': 'simple test',
        }
        response = self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        last_post = Post.objects.latest('pub_date')
        self.assertEqual(last_post.group, self.the_post.group)
        self.assertEqual(last_post.author, self.the_post.author)
        self.assertEqual(last_post.text, 'simple test')

    def test_post_edit(self):
        """Валидная форма редактирования поста"""
        another_group = Group.objects.create(
            title=GROUP_TITLE + ' 1',
            slug=GROUP_SLUG + '1',
            description=GROUP_DESCRIPTION
        )
        post_count = Post.objects.count()
        form_edit_data = {
            'group': another_group.pk,
            'text': self.the_post.text + ' 1',
        }
        response = self.authorised_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.the_post.pk}),
            data=form_edit_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.the_post.pk}))
        self.assertEqual(Post.objects.count(), post_count)
        edit_post = Post.objects.get(pk=self.the_post.pk)
        self.assertEqual(form_edit_data['text'], edit_post.text)
        self.assertEqual(another_group, edit_post.group)
        self.assertEqual(self.the_post.author, edit_post.author)



        self.assertTrue(
                    Post.objects.filter(
                        slug=GROUP_SLUG,
                        text=POST_TEXT,
                        image='posts/small.gif'
                    ).exists()
        )