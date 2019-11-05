from django.contrib import admin
from .models import Post
# Register your models here.

class PostModelAdmin(admin.ModelAdmin):
    list_display = ['id','title','slug','timestamp','draft','publish']
    list_display_links = ['slug']
    search_fields = ['title','content']
    list_filter = ['updated','timestamp']
    class Meta:
        model = Post

admin.site.register(Post,PostModelAdmin)