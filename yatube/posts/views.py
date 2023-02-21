from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.cache import cache_page
from requests import delete

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post, User, Follow


def get_page(request, post_list):
    paginator = Paginator(post_list, settings.POST_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all().select_related('author', 'group')
    page_obj = get_page(request, post_list)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = get_page(request, posts)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    template = 'posts/profile.html'
    page_obj = get_page(request, author_posts)
    following = True
    if request.user not in Follow.objects.all().select_related('user'):
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    form = CommentForm(request.POST or None,
                       files=request.FILES or None)
    posts_comments = Comment.objects.select_related('author', 'post')
    template = 'posts/post_detail.html'
    context = {'post': post,
               'form': form,
               'comments': posts_comments}
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    context = {'form': form}
    if not form.is_valid():
        return render(request, template, context)

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        return redirect('posts:post_detail', post_id)
    form.save()
    context = {
            'is_edit': True,
            'form': form,
            'post': post
    }
    template = 'posts/create_post.html'
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    following_posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page(request, following_posts)
    template = 'posts/follow.html'
    context = {
            'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('posts:profile', username=username)
