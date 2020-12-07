from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse




class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    # content = RichTextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    # likes= models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name='likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='dislikes')
    # dislikes= models.IntegerField(default=0)
    # preference = models.ForeignKey(Preference,on_delete=models.CASCADE)


    def __str__(self):
        return self.title

    def num_likes(self):
        return self.likes.all().count()

    def num_dislikes(self):
        return self.dislikes.all().count()

    def get_absolute_url(self):
        return reverse('post-detail',kwargs={'pk':self.pk})


class Comment(models.Model):
    content = models.TextField(max_length=150)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_connected = models.ForeignKey(Post, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('post-detail',kwargs={'pk':self.pk})


class Preference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + ':' + str(self.post) + ':' + str(self.value)

    class Meta:
        unique_together = ("user", "post", "value")