from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from .models import *


# Register your models here.
class TaggedItemInline(GenericStackedInline):
    model = TaggedItem
    extra = 1

# admin.site.register(TaggedItem)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "subtitle", "author", "created_on", "status")
    inlines = [TaggedItemInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "date_of_birth", "avatar", "bio")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # list_display = ("name", "parent", "tag_ptr")
    readonly_fields = ("slug",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', )

