from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, Http404
from .models import Post
from .forms import PostForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from comments.forms import CommentForm
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType


# Create your views here.
@login_required()
def post_create(request):
    title = 'Create'
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        'title': title,
        'form': form
    }
    return render(request, 'postform.html', context)


def post_list(request):
    today = timezone.now().date()
    object_list = Post.custom_filter.active()
    if request.user.is_staff or request.user.is_superuser:  # show all to staff or superuser
        object_list = Post.custom_filter.all()

    query = request.GET.get('q') # search
    if query:
        object_list = object_list.filter(
            Q(title__icontains=query)|
            Q(content__icontains=query)|
            Q(user__username__icontains=query)).distinct()

    paginator = Paginator(object_list, 2)  # Show 4 contacts per page
    page = request.GET.get('page')
    object_list = paginator.get_page(page)
    context = {
        'object_list': object_list,
        # 'object_list':contacts,
        'today': today
    }
    return render(request, 'postlist.html', context)


def post_detail(request, slug):
    today = timezone.now().date()
    object = get_object_or_404(Post, slug=slug)
    if object.draft or object.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    initial_data = {
        'content_type': object.get_content_type,
        'object_id': object.id
    }
    form = CommentForm(request.POST or None,initial=initial_data)
    if form.is_valid():
        # c_type = form.cleaned_data.get("content_type")
        # # content_type = ContentType.objects.get_for_model(c_type)
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs[0]
        new_comment, created = Comment.objects.get_or_create(
                            user= request.user,
                            content_type=object.get_content_type,
                            object_id = obj_id,
                            content = content_data,
                            parent = parent_obj )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())
    # comments = Comment.objects.filter_by_instance(object)
    comments = object.comments
    context = {
        'comments': comments,
        'object': object,
        'today': today,
        'comment_form':form,
    }
    return render(request, 'postdetail.html', context)


def post_update(request, slug):
    title = 'Update'
    object = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=object)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "-Updated")
        return HttpResponseRedirect(instance.get_absolute_url())
    else:
        messages.error(request, " form error! ")

    context = {
        'title': title,
        'object': object,
        'form': form
    }
    return render(request, 'postform.html', context)


def post_delete(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, ' Deleted ')
    return redirect('posts:post_list')
