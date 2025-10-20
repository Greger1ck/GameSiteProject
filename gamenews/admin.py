from django.contrib import admin

from gamenews.models import Category, Comment, Image, Tag, Post


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ('image', 'caption', 'alt_text', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug',)
    list_display_links = ('title',)
    prepopulated_fields = {'slug' : ('title',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug',)
    prepopulated_fields = {'slug' : ('title',)}
    order_by = ('title',)
    list_display_links = ('title',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    save_on_top=True
    readonly_fields = ('views',)
    prepopulated_fields = {'slug' : ('title',)}
    filter_horizontal = ['tag']
    list_display=['title','author','views']
    inlines = [ImageInline]

    def get_image_count(self, obj):
        return obj.images.count()
    get_image_count.short_description = "Кол-во изображений"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'date', 'verify']
    list_editable = ['verify',]
    list_display_links = ['author', 'post']



