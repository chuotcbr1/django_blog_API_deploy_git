
from django.urls import path
from .views import post_list,post_detail,post_create,post_update,post_delete
app_name = 'posts'

urlpatterns = [
    path('',post_list,name='post_list'),
    path('create/',post_create,name='post_create'),
    path('detail/<slug>/',post_detail,name='post_detail'),
    path('update/<slug>/',post_update,name='post_update'),
    path('delete/<slug>/',post_delete,name='post_delete'),
]
