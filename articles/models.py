from django.db import models
from django_resized import ResizedImageField

# Create your models here.

subject_list = [
        ('일반','일반'),
        ('건의사항','건의사항'),
        ('오류제보','오류제보'),
]

class Article(models.Model):

    title = models.CharField(max_length=80)
    content = models.TextField()
    createuser = models.CharField(max_length=80)
    password = models.CharField(max_length=80)
    hits_field = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)
    subject = models.CharField(max_length=50, choices=subject_list)
    
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):
    
    content = models.TextField()
    createuser = models.CharField(max_length=80)
    password = models.CharField(max_length=80)
    article = models.ForeignKey(Article,null=False, blank=False, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    def __str__(self):
        return self.content

class PostImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='image')
    image = ResizedImageField(size=[1000,1000],upload_to="image", null=True, blank=True)
    image_original = models.ImageField(upload_to="image", null=True, blank=True)
