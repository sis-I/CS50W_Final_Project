from django.http import HttpResponseBadRequest
from blog.models import BlogPost


def owner_required(func):
    def wrapper(request, post_id=None, *args, **kwargs):
        if post_id is not None:
            post = BlogPost.objects.get(id=post_id)
            if request.user != post.author:
                return HttpResponseBadRequest()

        return func(request, post_id, *args, **kwargs)
    
    return wrapper
