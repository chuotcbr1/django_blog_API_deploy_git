from django.db import models
from django.urls import reverse
import os
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from markdown_deux import markdown
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class PostManager(models.Manager):
    def active(self,*args,**kwargs):
        return super(PostManager,self).filter(publish__lte=timezone.now()).filter(draft=False)
    def all(self,*args,**kwargs):
        return super(PostManager,self).all()


def upload_location(instance, filename):
    return os.path.join('%s/%s/%s' % (instance.__class__.__name__,instance.title, filename))

class Post(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField(null=True)
    image = models.ImageField(null=True,blank=True,upload_to=upload_location,
                              height_field = "height_field",
                              width_field = 'width_field')
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    content = models.TextField()
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now_add=False,auto_now=False)
    updated = models.DateTimeField(auto_now_add=False,auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True,auto_now=False)

    custom_filter = PostManager()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:post_detail',kwargs={'slug':self.slug})
    def get_update_url(self):
        return reverse('posts:post_update',kwargs={'slug':self.slug})

    class Meta:
        ordering = ['-timestamp','-updated']

    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type

def create_slug(instance,new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.custom_filter.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:

        new_slug = "%s-%s"%(slug,qs[0].id)
        print(new_slug)
        return create_slug(instance,new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender,instance,*args,**kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver,sender=Post)