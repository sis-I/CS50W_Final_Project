from django.contrib import admin

from django.contrib.contenttypes.admin import GenericStackedInline

from .models import User
from blog.models import TaggedItem

class TaggedItemInline(GenericStackedInline):
    model = TaggedItem
    extra = 1

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline]
    # list_display = ("")