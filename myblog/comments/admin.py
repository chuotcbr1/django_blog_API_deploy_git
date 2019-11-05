from django.contrib import admin
from .models import Comment
# Register your models here.

class CommentModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','timestamp']
    list_display_links = ['id']
    list_filter = ['timestamp']
    class Meta:
        model = Comment

admin.site.register(Comment,CommentModelAdmin)