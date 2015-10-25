from django.contrib import admin
from rango.models import Category, Page

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields' : ['name']}),
        ('Views, Likes', {'fields': ['views', 'likes']})
    ]
    prepopulated_fields = {'slug':('name',)}


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)