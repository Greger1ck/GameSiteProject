from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from bot import send_message


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название", db_index=True)
    slug = models.SlugField(unique=True, verbose_name="Слаг")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название", db_index=True)
    slug = models.SlugField(unique=True, verbose_name="Слаг")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название", db_index=True)
    slug = models.SlugField(verbose_name="Слаг", unique=True, default="")
    shot_description = models.TextField(verbose_name="Краткое описание")
    full_description = models.TextField(verbose_name="Полное описание")
    anons_picture = models.ImageField(
        verbose_name="Картинка анонса", upload_to="posts_image", null=True, blank=True
    )
    body_picture = models.ImageField(
        verbose_name="Картинка", upload_to="posts_image", null=True, blank=True
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Автор",
    )
    views = models.IntegerField(verbose_name="Просмотры", default=0)
    published_date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(
        to=Category,
        verbose_name="Категория",
        related_name="posts_by_cat",
        on_delete=models.CASCADE,
    )
    tag = models.ManyToManyField(
        to=Tag, verbose_name="Теги", related_name="posts_by_tag"
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def get_absolute_url(self):
        return reverse("post", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(verbose_name="Текст комментария")
    date = models.DateField(verbose_name="Дата", auto_now_add=True)
    author = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comment_by_user",
        verbose_name="Автор",
    )
    post = models.ForeignKey(
        to=Post,
        related_name="comments_by_post",
        on_delete=models.CASCADE,
        verbose_name="Пост",
    )
    verify = models.BooleanField(default=False, verbose_name="Проверен?")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.author} - {self.post.title}"
    

@receiver(post_save, sender=Comment)
def new_comment_create(sender, instance: Comment, created, **kwargs):
    if created:
        send_message(f'''У нас новый комментарий!
<b>ОТ</b>: {instance.author.username}
<b>ПОСТ</b>: {instance.post.title}
<b>ТЕКСТ</b>:
<code>{instance.text}</code>
<b>ДАТА</b>: {instance.date}
''', instance.id)
