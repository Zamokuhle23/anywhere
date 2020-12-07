from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView

                                  )
from django_ajax.decorators import ajax

from .forms import NewCommentForm
from .models import Post, Comment, Preference
# class TrendListView(ListView):
#     model = Post
#     template_name = 'blog/home.html'
#     context_object_name = 'posts'
#
#     ordering = ['-likes']

@login_required
def Home(request):
    content = Post.objects.all().order_by('-date_posted')
    preference = Preference.objects.all()

    context = {
        "content":content,
        "preference":preference
    }

    return render(request, 'blog/home.html', context)




class PostListView(LoginRequiredMixin,ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'

    ordering = ['date_posted']

    def get_queryset(self):
        '''
        building a dynamic Queryset
        '''
        queryset = Post.objects.all().all().order_by('-date_posted')
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(author__username__icontains=query) |
                Q(title__icontains=query) |
                Q(content__icontains=query)
            ).distinct()
        return queryset


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_post.html'
    context_object_name = 'posts'

    def get_queryset(self):
        user = get_object_or_404(User,username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = NewCommentForm(instance=self.request.user)
        return data

    def post(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                              author=self.request.user,
                              post_connected=self.get_object())
        new_comment.save()

        return self.get(self, request, *args, **kwargs)



class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    fields = ['title','content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ['title','content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    success_url = '/home'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class CommentUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Comment
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False


class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Comment
    success_url = '/'
    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False



def postpreference(request, postid, userpreference):
    print(postid)
    if request.method == "POST":
        eachpost = get_object_or_404(Post, id=postid)
        user = request.user
        obj = ''

        valueobj = ''

        try:
            obj = Preference.objects.get(user=request.user, post=eachpost)

            valueobj = obj.value

            valueobj = int(valueobj)

            userpreference = int(userpreference)

            if valueobj != userpreference:
                obj.delete()

                upref = Preference()
                upref.user = request.user

                upref.post = eachpost

                upref.value = userpreference

                if userpreference == 1 and valueobj != 1:
                    eachpost.likes.add(user)
                    eachpost.dislikes.remove(user)
                elif userpreference == 2 and valueobj != 2:
                    eachpost.dislikes.add(user)
                    eachpost.likes.remove(user)

                upref.save()

                eachpost.save()
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            elif valueobj == userpreference:
                obj.delete()

                if userpreference == 1:
                    eachpost.likes.remove(user)
                elif userpreference == 2:
                    eachpost.dislikes.remove(user)

                eachpost.save()
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except Preference.DoesNotExist:
            upref = Preference()

            upref.user = request.user

            upref.post = eachpost

            upref.value = userpreference

            userpreference = int(userpreference)

            if userpreference == 1:
                eachpost.likes.add(user)
            elif userpreference == 2:
                eachpost.dislikes.add(user)

            upref.save()

            eachpost.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # return render('home/')





def about(request):
    return render(request, 'blog/about.html')