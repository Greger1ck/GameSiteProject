from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import F, Q, Case, CharField, Count, Max, Value, When
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
import requests
import json

from gamenews.forms import AddPostForm, CommentForm
from gamenews.models import Category, Comment, Post, Tag

VSEGPT_KEY = "sk-or-vv-baa39a11afa2312de2d0521d678334d4dcb4cbedb8ea64aa1f606e42236270c2"

def check_comment_with_AI(text):

    question = f'''Ты - ИИ-модератор сайта для комментариев.
    Контекст: Комментарий должен быть без оскорблений, без мата, не упоминать политику и не содержать призывов к наслилию.
    Оцени этот комментарий: {text}.
    Ответь: true если комментарий прошёл проверку, или false если не прошёл.'''

    response = requests.post(
        "https://api.vsegpt.ru/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {VSEGPT_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-5-nano",
            "messages": [{"role": "user", "content": question}]
        }
    )

    response_data = response.json()
    print(response_data)
    msg = response_data["choices"][0]["message"]["content"]

    if msg.lower() == 'true':
        return True
    return False



class IndexPage(ListView):
    model = Post
    template_name = "gamenews/index.html"
    context_object_name = "posts"
    paginate_by = 3

    def get_queryset(self):
        if self.request.GET:
            if "search" in self.request.GET:
                query = self.request.GET["search"]
                return Post.objects.filter(
                    Q(title__icontains=query) | Q(full_description__icontains=query)
                )
        return Post.objects.annotate(rat=Case(
            When(views__gt=100, then=Value('Высокий')),
            When(views__gt=50, then=Value('Средний')),
            When(views__gt=10, then=Value('Низкий')),
            default=Value('Начальный'),
            output_field=CharField()
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Главная страница"
        context["count"] = self.get_queryset().count()
        context["anno"] = Category.objects.annotate(total=Count("posts_by_cat"))
        if self.request.GET:
            if "search" in self.request.GET:
                context["search"] = self.request.GET["search"]
        return context


class DetailPost(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "gamenews/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context["comments"] = post.comments_by_post.filter(verify=True)
        context["title"] = post.title
        context["rel_posts"] = (
            Post.objects.select_related("category")
            .prefetch_related("tag")
            .filter(category=post.category)
            .order_by("?")[:3]
        )
        context["best_cats"] = Category.objects.annotate(
            total=Count("posts_by_cat")
        ).order_by("-total")[:5]
        context['last_post'] = Post.objects.order_by('-published_date')[:3]

        return context

    def get(self, request, *args, **kwargs):        
        form = CommentForm()
        self.object = self.get_object()
        Post.objects.filter(pk=self.object.pk).update(views=F("views") + 1)
        self.object.refresh_from_db()
        my_context = self.get_context_data(object=self.object)
        my_context["form"] = form
        

        return self.render_to_response(context=my_context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            author = request.user
            check_AI = ''
            if author.username == "admin":
                verify = True
            else:
                verify = check_comment_with_AI(form.cleaned_data["text"])
                check_AI = ' (Проверено с ИИ)'
                
            Comment.objects.create(
                post=self.object,
                author=author,
                text=form.cleaned_data["text"] + check_AI,
                verify=verify,
            )
            return redirect(self.object.get_absolute_url())
        context = self.get_context_data(form=form)
        return self.render_to_response(context=context)

    def post_list(request):
        posts = Post.objects.all()
        return render(request, 'gamenews/post_list.html', {'posts': posts})

    def post_detail(request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        # post.images.all() получит все изображения, связанные с этим постом
        print(post.images.all())
        return render(request, 'gamenews/post_detail.html', {'post': post})
    
class AddPostView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = AddPostForm
    template_name = "gamenews/form_add.html"

    def form_valid(self, form):
        new_post = form.save(commit=False)
        new_post.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создание поста"
        return context


class UpdatePostView(UpdateView):
    model = Post
    fields = ["title", "shot_description", "full_description"]
    template_name = "gamenews/form_add.html"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Изменение поста"
        return context


class About(TemplateView):
    template_name = "gamenews/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "О нас"
        return context


class CategoryView(ListView):
    model = Category
    template_name = "gamenews/category_all.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.annotate(post_count=Count("posts_by_cat"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Все категории"
        return context


class CategoryDetailView(ListView):
    model = Post
    template_name = "gamenews/category.html"
    context_object_name = "post_cats"

    def get_queryset(self):
        query_set = super().get_queryset()
        cat = Category.objects.get(slug=self.kwargs["slug"])
        return query_set.filter(category__pk=cat.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat"] = Category.objects.get(slug=self.kwargs["slug"])
        context["title"] = context["cat"]
        return context


def post_list(request):
    # Получаем все категории и теги для отображения в фильтрах
    categories = Category.objects.all()
    tags = Tag.objects.all()

    # Получаем все посты по умолчанию
    posts = Post.objects.all()

    # Получаем выбранную категорию из GET-параметров
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
        print(posts)
    # Получаем выбранные теги из GET-параметров
    tag_ids = request.GET.getlist('tag') # getlist используется, потому что тегов может быть несколько
    if tag_ids:
        # Фильтруем по тегам. filter(pk__in=tag_ids) выбирает теги по их ID
        # .distinct() удаляет дубликаты постов, если пост имеет несколько выбранных тегов
        posts = posts.filter(tag__slug__in=tag_ids).distinct()

    context = {
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'selected_category': category_slug, # Передаем выбранную категорию в шаблон
        'selected_tags': tag_ids,           # Передаем выбранные теги в шаблон
    }
    return render(request, 'gamenews/post_list.html', context)
