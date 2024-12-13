import json
import datetime

from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page

from django.db.models import Count

from accounts.models import User
from .models import (BlogPost, UserProfile, Category, 
                     Comment, Tag, TaggedItem, BlogBookmark, 
                     BlogHistory)
from .forms import BlogPostForm, CommentForm

from .custom_decorators.decorators import owner_required

# Create your views here.

def index(request):
    ''' 1. For annonymous user:
          View Trending Posts: use the most recent posts with in this week,
          then use number of likes ,
          then number of read history, then number of 
        2. For signed in  user:
         2.1 'For You' page: view posts from author 
                - previously liked, read, bookmarked & followed by current user
                - and in addition posts with tags the current user interested in
                - and this week trending post
         2.2 '?feed=following' page: view posts from author the current user follows
         2.3 'tag=<tag slug>' page: view posts with a <tag> the current user interested in
    '''
    # Current User
    user = request.user

    now = timezone.now()
    weektime = now - datetime.timedelta(days=7) # With in a week(7 days)

    if not user.is_authenticated:

        #  Get this week's trending posts limted to 5 posts
        trending_posts = BlogPost.all_published.annotate(
                                    tot_likes=Count('like_users'), 
                                    tot_read=Count('reading_history')
                                    ).filter(
                                        published_on__gte=weektime,
                                    ).order_by('-tot_likes', '-tot_read')[:5] 
            
        # Get most read posts 
        most_read_posts = BlogPost.all_published.select_related(
                                        'author', 'author__profile'
                                    ).prefetch_related(
                                        'bookmarks', 'tags', 
                                        'tags__topic_followers'
                                    ).annotate(
                                        tot_read=Count('reading_history'),
                                        tot_tags_followers=Count('tags__topic_followers')
                                    ).order_by('-tot_read', '-tot_tags_followers')
        
        # Get tags from most read posts
        tags = Tag.objects.filter(
                                id__in=most_read_posts[:6].values_list('tags__tag', flat=True)
                            )

        return render(request, "blog/index.html", {
            "trendings": trending_posts,
            "posts": most_read_posts,
            'tags': tags
        })

    # Dashboard view when user is signed in,
    else:
        # Topics the user is interested in        
        interests = TaggedItem.objects.select_related(
                                    'tag'
                                    ).prefetch_related(
                                        'similar_posts'
                                    ).filter(topic_followers=user)
        
        three_days_before = now - datetime.timedelta(days=3)

        # Latest Trending posts with in atleast three days
        latest_trending_posts = BlogPost.all_published.select_related(
                                            'author', 'author__profile',
                                        ).prefetch_related(
                                            'tags', 'tags__tag', 'like_users', 'reading_history'
                                        ).annotate(
                                            tot_likes=Count('like_users', distinct=True),
                                            tot_read=Count('reading_history', distinct=True)
                                        ).filter(
                                            published_on__gte=three_days_before,
                                        )
        
        # Get Latest trending posts' tags/topics  
        recommended_topics= Tag.objects.filter(
                                id__in=latest_trending_posts.order_by().values_list('tags__tag')
                            )[:9]

        recent_bookmarks = BlogBookmark.objects.select_related(
                                                'bookmark_post',
                                            ).filter(
                                                bookmark_by=user,
                                                created_on__gte=three_days_before
                                            )
        
        # Initial context
        context = {
            'interests' : interests,
            'latest_trending_posts': latest_trending_posts[:5], # only five posts
            'recommended_topics': recommended_topics,
            'recent_bookmarks': recent_bookmarks,
        }


        feed = request.GET.get('feed')
        tag =  request.GET.get('tag')
 
        if feed == "following":
            # template_name = "blog/dashboard.html"
            posts = BlogPost.all_published.select_related(
                                        'author', 'author__profile'
                                    ).prefetch_related(
                                        'author__followings',
                                        'like_users'
                                    ).filter(author__in=user.followings.all())

            context.update({'posts': posts, 'section': 'following'})

        # POSTS UNDER CURRENT USER INTERESTS in Dashboard page
        elif tag:
            # Query for posts filter from tag slug
            posts = BlogPost.all_published.select_related(
                                                'author', 'author__profile'
                                            ).prefetch_related(
                                                'tags', 'like_users', 'bookmarks'
                                            ).filter(
                                                tags__tag__slug=tag
                                            )
            # Update context
            context.update({'posts': posts, 'section': tag})
        else:
            # Simple database query to list blog posts for the particular user
            
            # Other posts from users previously liked by current user
            # Get author of liked user
            liked_authors =  user.liked_posts.order_by().values_list('author', flat=True) #user.liked_posts.values_list()
           
            # Posts from users followed by current user
            followed_authors = user.followings.values_list('id', flat=True)
            
            
            # Posts from user once viewed/reacted on by this current user
            read_authors = user.read_history_posts.order_by().values_list('author', flat=True)
            
            # Posts from user previously bookmarked by this current user
            bookmarked_authors = user.bookmarked_posts.order_by().values_list('author', flat=True)
           
            # Combined authors 
            authors = liked_authors.union(followed_authors, read_authors, bookmarked_authors)

            # TODO: posts recommended by the admin
            # This week trending posts 
            trending_posts = BlogPost.all_published.select_related(
                                        'author', 'author__profile'
                                    ).prefetch_related(
                                        'tags', 'bookmarks', 'like_users', 'reading_history'
                                    ).annotate(
                                        tot_likes=Count('like_users'), 
                                        tot_read=Count('reading_history')
                                    ).filter(
                                        published_on__gte=weektime,
                                    ).order_by('-tot_likes', '-tot_read') 
            
            # posts from users the current user interested in topics
            interest_posts = BlogPost.all_published.select_related(
                                                        'author', 'author__profile'
                                                    ).prefetch_related(
                                                        'tags', 'bookmarks', 'like_users', 'reading_history'
                                                    ).filter(
                                                        tags__tag__in=interests.values_list('tag')
                                                    )
            
            
            posts = BlogPost.all_published.select_related(  
                                                'author', 'author__profile'
                                            ).prefetch_related(
                                                'tags', 'bookmarks', 'like_users', 'reading_history'
                                            ).filter(
                                                # Union authors of followed authors,
                                                # authors of previously liked posts,
                                                # authors of previously read posts
                                                # and authors of previously bookmarked posts
                                                author__in=authors,
                                            ).annotate(
                                                tot_likes=Count('like_users'),
                                                tot_bookmarks=Count('bookmarks'),
                                                tot_read=Count('reading_history'),
                                            ).order_by(
                                                # '-published_on',
                                                '-like_users',
                                                '-tot_bookmarks',
                                                '-tot_read',
                                            )
            
            # Combine posts with posts with tags the current user interested in
            posts = posts | interest_posts

            # Again Combine with this week trending posts 
            posts = posts | trending_posts
            
            # For you posts list context  
            context.update({'posts': posts, 'section': 'dashboard'})

        return render(request, "blog/dashboard.html", context=context)


def post_detail(request, year, month, day, post_slug):
    #TODO Check if memebers-only permissions required + LOGIN
    
    try:
        # GET FOR PUBLISHED POST, USING PUBLIHED DATE AND SLUG
        post = BlogPost.all_published.select_related(
                                                'author', 'author__profile',
                                            ).prefetch_related(
                                                'like_users', 'tags', 'comments',
                                                'bookmarks', 'reading_history'
                                            ).get(
                                                published_on__year=year, 
                                                published_on__month=month, 
                                                published_on__day=day,
                                                slug=post_slug
                                            )

        status = 'public' # as the post is published
        
    except Exception as e:
        print(e)
        return HttpResponse("Error: No such public post available!")
    
    user = request.user
    is_auth = user.is_authenticated

    # Check if bookmarked by the login user
    bookmarked = False
    if is_auth and post.bookmarks.filter(id=user.id).exists():
        bookmarked = True

    # Check if post added in reading history by the login user 
    if user.is_authenticated and not post.reading_history.filter(
                                                                id=user.id
                                                            ).only('id').exists():
        post.reading_history.add(user)

    comments = Comment.objects.filter(
                    post=post, 
                    parent=None,
                    active=True
                ).annotate(total=Count('like_users')).order_by('-total')

    # Get other posts from the author
    author_posts = BlogPost.all_published.filter(
                                author=post.author
                            ).exclude(slug=post.slug)[:5]
    
    return render(request, "blog/detail_post.html", {
        "post": post,
        "author_posts": author_posts,
        "status": status,
        "comments": comments,
        "comment_form": CommentForm(),
        "bookmarked" : bookmarked,
    })


@owner_required
@login_required
def write_or_edit_story(request, post_id=None, status=None):
    """ Write a story when there is no post created hence No post_id,
        Edit post when 'post_id' is already created first
        Update post if post published previously
    """
    if post_id is None:
        form = BlogPostForm(request.POST or None) #, request.FILES or None

        if request.method == "POST":
            
            tag_names = request.POST.getlist('tag')

            if form.is_valid():
                post = form.save(commit=False)
                
                post.author = request.user
                post.featured_image = request.FILES.get('featured_image')
                post.featured_image_caption = request.POST.get('featured_image_caption')
                
                post.save() # Just save to draft

                for tag_name in tag_names:
                    tag = Tag.objects.get_or_create(name=tag_name)[0]
                    # instance.tags.create(tag=tag)
                    tagged_item = TaggedItem(content_obj=post, tag=tag)
                    tagged_item.save()
            
                if "self-publish" in request.POST:
                    """Own publishing"""
                    post.status = "published"
                    post.save()
    
                    # TODO - Some alert that the post is published
                    # return HttpResponse("Self Published")
                    return HttpResponseRedirect(post.get_absolute_url())
                
                # elif "submit-to-publisher" in request.POST and post.status != "published":
                #     """ Send the draft to publishers """
                #     post.status = "draft_submitted"
                #     post.save()
                #     # TODO - LIST PUBLICATION THE USER IS MEMEBER OF AND CHOOSE ONE USER WANT
                #     # THIS POST BE PUBLISHED
                #     return HttpResponse("Send to Publisher")              
                
                return HttpResponseRedirect(reverse("blog:edit_story", args=(post.id,)))

        return render(request, "blog/create_or_edit_post.html", {
            "form": form,
            "url": "new-story",
            # "post_id": "",
        })
    
    else:
        # Edit Story
        post = get_object_or_404(BlogPost, pk=post_id)
        url = "edit"
        message = "No change done"
        
        if request.method == "POST":
            form = BlogPostForm(request.POST, instance=post)

            tag_names = request.POST.getlist('tag')
            
            prev_tag_names = post.tags.select_related(
                                                    'tag'
                                                ).values_list('tag__name', flat=True)

            # Loop through to add input tag names                                      
            for tag_name in tag_names:
                if tag_name not in prev_tag_names:
                    # Create tag if not exist
                    tag = Tag.objects.get_or_create(name=tag_name)[0]
                    post.tags.create(tag=tag)

            # Make sure form has been changed
            if form.is_valid() and form.has_changed():
                message = "Change saved."            
                post = form.save(commit=False) # Updated to instance, if any change

            new_updates = {
                'featured_image': request.FILES.get('featured_image'),
                'featured_image_caption': request.POST.get('featured_image_caption')
            }

            for field, new_value in new_updates.items():

                if new_value and getattr(post, field) != new_value:
                    setattr(post, field, new_value)

            post.save()

            if "self-publish" in request.POST:
    
                post.status = "published"
                post.save()

                return HttpResponseRedirect(reverse("blog:post-detail", args=(
                    post.pub_year,
                    post.pub_month,
                    post.pub_day,
                    post.slug
                )))
            
            # Update the public story
            elif "update-story" in request.POST and status == 'public':
                return HttpResponseRedirect(reverse("blog:post-detail", args=(
                    post.pub_year,
                    post.pub_month,
                    post.pub_day,
                    post.slug
                )))

            return render(request, "blog/create_or_edit_post.html", {
                "form": form,
                "url": url,
                "post_id": post_id,
                "prev_tags": [t.tag.serialize() for t in post.tags.all()],
                "message": message,
            })

        return render(request, "blog/create_or_edit_post.html", {
            "form": BlogPostForm(instance=post),
            "post": post,
            "prev_tags": [t.tag.serialize() for t in post.tags.all()],
            "url": url,
            "status": status,
            "post_id": post_id,
        })


@owner_required
@require_POST       
@login_required
def delete_story(request, post_id):
    """ API request for deleting post owned by the user
    """
    post = get_object_or_404(BlogPost, pk=post_id)
    status = post.status
    post.delete()
    
    return (
        JsonResponse({
            'success': 'Draft post was successfully deleted!'
        }) if status == "draft_unsubmitted" else HttpResponseRedirect(reverse('blog:home'))
    )


def profile_view(request, username):
    """ Profile View
    """
    user = request.user

    try:
        profile_user = User.objects.prefetch_related(
                                                        "followers", "followings",
                                                        "bookmarked_posts", 'read_history_posts'
                                                    ).get(username=username)
        
        # For time being, If requesting user is not profile_user not need to check bookmark
        has_bookmark = False

        if profile_user == user:
            # Get obj in a tuple at index 0
            profile = UserProfile.objects.get_or_create(user=profile_user)[0]
            bookmarked_posts = profile_user.bookmarked_posts.all()
            has_bookmark = bookmarked_posts.exists()
        else:
            profile = UserProfile.objects.get(user=profile_user)

    except Exception as e:
        print(e)
        return HttpResponse("Nothing to show here!!")
    
    return render(request, "blog/profile.html", {
        "posts": BlogPost.all_published.filter(author=profile_user),
        "profile_user" : profile_user,
        "username": username,
        "profile": profile,
        'has_bookmark': has_bookmark,
    })


def profile_lists_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    if request.user == profile_user:
        bookmarked_posts = profile_user.bookmarked_posts.all()
        has_bookmark = bookmarked_posts.exists()

        return render(request, "blog/profile_lists.html", {
            "profile_user": profile_user,
            "username": username,
            "bookmarked_posts": bookmarked_posts,
            "profile": UserProfile.objects.get(user=profile_user),
            "has_bookmark": has_bookmark,
        })


@login_required
def create_or_edit_profile(request, username):
    user = get_object_or_404(User, username=username)   
    
    try:
        user_profile = UserProfile.objects.get_or_create(user=user)[0] # Tuple of index 0

    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!!")

    if request.method == "POST":
        new_updates = {
            'avatar': request.FILES.get('avatar'),
            'date_of_birth': request.POST.get('date_of_birth') or None,
            'bio': request.POST.get('bio'),
        }

        # Make sure if changes have taken place,
        for field, new_value in new_updates.items():
            # Check if we have new input and different from previous, 
            # replace with the new one.
            if getattr(user_profile, field) != new_value:
                setattr(user_profile, field, new_value)
        
        # Save changes if any
        user_profile.save()

        return HttpResponseRedirect(reverse("blog:user-profile-about", args=(username,))) 
        

    elif request.method == 'GET':
        #  Owner Permission Required
        if request.user.username != username:
            return HttpResponse("You have no permission to edit!")
        
        return JsonResponse(user_profile.serialize())
    

def profile_about_view(request, username):

    # Query for user of which their profile to be viewed
    profile_user = get_object_or_404(User, username=username)

    has_bookmark = profile_user.bookmarked_posts.all().exists()
    try:
        profile = get_object_or_404(UserProfile, user=profile_user)
    except Exception as e:
        print(e)
        return render(request, "blog/profile_about.html", {
            "profile": None,
            "profile_user": profile_user,
            "username": username,
            "has_bookmark": has_bookmark,
        })
    
    return render(request, "blog/profile_about.html", {
        "profile": profile,
        "profile_user": profile_user,
        "username": username,
        "has_bookmark": has_bookmark,
    })


def followings_view(request, username):
    user = User.objects.get(username=username)

    return render(request, "blog/following_list.html", {
        'followings': user.followings.all(),
        'username': username,
    })



def followers_view(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "blog/follower_list.html", {
        "followers": user.followers.all(),
        'username': username
    })


def category_list(request):
    return render(request, "blog/category_list.html", {
        'categories': Category.objects.select_related(
                                        'parent'
                                    ).prefetch_related(
                                        'children'
                                    ).filter(parent=None),
    })


def tagged_posts(request, slug):
    ''' List posts with same tag slug/name in a page. And check if that tag is followed by current 
        user or not
    '''
    try:    
        tag = Tag.objects.get(slug=slug)
        similar_posts = BlogPost.all_published.select_related(
                                        'author', 'author__profile'
                                    ).prefetch_related(
                                        'tags', 'tags__tag', 'bookmarks'
                                    ).filter(tags__tag=tag)

        # Get number of followers to this tag
        topic_followers = User.objects.prefetch_related(
                                    'interests',
                                    ).filter(interests__tag=tag)

    except Exception as e:
        print(e)
        return HttpResponse("There is no such tag slug!!")

    category = None
    try:
        category = Category.objects.select_related('parent')\
                            .prefetch_related('children').get(slug=slug)
    except Exception as e:
        print(e)
        pass
    
    return render(request, "blog/tagged_post_list.html", {
        "tag": tag,
        "tag_slug": slug,
        "category": category or None,
        "posts": similar_posts,
        "topic_followers": topic_followers,
    })


@login_required
def search_modal_result(request):
    q = request.GET.get('q')

    if q:
        # Return three tag result
        tags = Tag.objects.filter(name__startswith=q)[:3]

        # Return threr users result
        people = User.objects.filter(
                                        username__startswith=q
                                    ).exclude(
                                            username=request.user.username
                                    ).only('username')[:3]
        
        # Most recent three posts 
        posts = BlogPost.all_published.filter(
                                            title__icontains=q,
                                        ).only('title')[:3]
            
        return JsonResponse({
            'success': 'Search suggestion was found',
            'people': [person.username for person in people if people],
            'tags': [{'name': tag.name, 'slug': tag.slug} for tag in tags],
            'posts': [{'title': post.title, 'abs_url': post.get_absolute_url()} for post in posts],
            })



@login_required
def search_results_view(request, query_on='posts'):
    q = request.GET.get('q')
    if q:
        # Get posts results
        posts = BlogPost.all_published.filter(
                                            title__icontains=q,
                                         )
        # Get users result
        people = User.objects.filter(
                                    username__startswith=q
                                ).exclude(
                                        username=request.user.username
                                )
        # Get tags result
        tags = Tag.objects.filter(name__icontains=q)

        context = {
            'query_on': query_on, 
            'query': q, 
            'posts_count': posts.count(),
            'users_count': people.count(),
            'tag_count': tags.count(),
            }
        
        if query_on == 'posts':
            # query_on = 'posts'
            context.update({'posts': posts })
        elif query_on == 'people':
            context.update({'users': people})
        elif query_on == 'topics':
            context.update({'tags': tags})

        return render(request, 'blog/search_results.html', context=context)

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def follow_or_unfollow(request, username):
    """API requests to follow user or unfollow
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data['action']
        user = get_object_or_404(User, username=username)
        follower_user = request.user

        if action == 'follow' and follower_user != user:
            follower_user.followings.add(user)
        elif action == 'unfollow' and follower_user != user:
            follower_user.followings.remove(user)
            
        return JsonResponse({'success': 'ok'})


@login_required
def like_or_unlike_post(request, post_id):
    '''- PUT request from client side will like or unlike the pareticular post,
    identified by post id, based on previous like status of the post by the user
    and return 'success' json response.
    '''
    post = get_object_or_404(BlogPost, pk=post_id)
    user = request.user 

    if request.method == 'PUT':
        data = json.loads(request.body)
        action = data['action']
        if action == 'like':
            post.like_users.add(user)
            return JsonResponse({'success': "Toggling like successful"})
        
        elif action == 'unlike':
            post.like_users.remove(user)
            return JsonResponse({'success': "Toggling unlike successful"})

    return JsonResponse({'error': 'Error has occured on toggling like/unlike!'})


@require_POST
@login_required
def add_or_remove_bookmark(request, post_id):
    '''Toggle Add or Remove bookmarks, fetching json data
    '''
    try:
        post = BlogPost.all_published.prefetch_related(
            'bookmarks'
            ).get(pk=post_id)
        
        user = request.user
        bookmarked = post.bookmarks.filter(id=user.id).exists()
        
        # Use json data fetching
        data = json.loads(request.body)
        action = data['action']

        if not bookmarked and action == 'bookmark':
            post.bookmarks.add(user)
            return JsonResponse(
                {'success' : 'Bookmark add was successful!'}
            )  
            
        elif bookmarked and action == 'unbookmark':
            post.bookmarks.remove(user) # Remove from bookmark
            return JsonResponse(
                {'success' : 'Bookmark remove was successful!'}
            )  

    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!!")

    
    return JsonResponse(
        {'error' : 'Bookmark add or remove was NOT successful!'}, 
        status=400
    )  


@login_required
def publish_comment(request): 
    # TODO if parent_id the comment will be reply
    form = CommentForm(request.POST)

    if request.method == 'POST':
        post_id = request.POST.get('post_id')

        if form.is_valid:
            comment = form.save(commit=False)
            comment.author  = request.user
            comment.post = get_object_or_404(BlogPost, pk=post_id)
            comment.active = True
            comment.save()

        return JsonResponse({'success': 'Comment was published successfully', 
                             "status": 200, 'comment_id': comment.id})
    
    return JsonResponse({'error': 'Something went wrong!!'}, status=403)


@require_POST
@login_required
def delete_comment(request, comment_id):
    ''' Delete a single comment when user signed in and 
        when request method is POST
    '''
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()

    return JsonResponse({'success': 'Comment was successfully deleted!'})


@login_required
def toggle_like_comment(request, comment_id):
    ''' User who is singed in can like or unlike comment when request
        method is 'PUT' and return success json respnse
        if failed return error in json response
    '''
    comment = get_object_or_404(Comment, pk=comment_id)
    user = request.user

    if request.method == 'PUT':
        data = json.loads(request.body)
        action = data['action']
        if action == 'like':
            comment.like_users.add(user)
        else:
            comment.like_users.remove(user)
        return JsonResponse({'success': 'Toggling like/unlike was successful!'})

    return JsonResponse({'error': "Error on Like/Unlike toggling!"})


@require_POST
@login_required
def reply_comment(request, comment_id):
    """ This is to reply comment on other comments, with requests and
        responses
    """
    if request.method == "POST":
        try:
            comment = Comment.objects.get(id=comment_id)
        except Exception as e:
            print(e)
            return HttpResponse('No comment available!')
        
        body = request.POST.get('body')
        post_id = request.POST.get('post_id')
        post = get_object_or_404(BlogPost, pk=post_id)

        reply = Comment(parent=comment, post=post, author=request.user, body=body)
        reply.active = True
        reply.save()
        
        comment.replies.add(reply)

        return JsonResponse({
            'success': 'Reply on comment was successfull!',
            'comment_id': reply.id
        })

    return JsonResponse({'error': 'Reply was not successful!'})


@login_required
def toggle_topic_follow(request, tag_slug):
    """ This is to toggle Topic follow/unfollow API POST requests and
        responses
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data['action']

        tag = get_object_or_404(Tag, slug=tag_slug)
        follower_user = request.user

        # topic_followers = User.objects.filter(interests__tag__slug=tag_slug)
        prev_tagged_items = TaggedItem.objects.select_related(
                                                'tag'
                                                ).filter(tag=tag,  
                                                    topic_followers=follower_user
                                                )

        # Or 'and follower_user not in topic_followers:
        if action == 'follow'  and prev_tagged_items.count() == 0: 
            follower_user.interests.add(TaggedItem(tag=tag), bulk=False)
            
            return JsonResponse({'success': "Follow action successful!"})
  
        # Or 'and follower_user in topic_followers:'
        elif action == 'unfollow' and prev_tagged_items.count() == 1: 
            follower_user.interests.remove(prev_tagged_items[0]) 

            return JsonResponse({'success': "Unfollow action successful!"})
        
    return JsonResponse({'error': "Following/Unfollowing Topic was not successfull!"})


@login_required
def library(request, lists_type='bookmarks'):
    '''List bookmarked posts when "lists_type" is "bookmarks"
        List posts read by this user when "lists_type"  is "reading-history"
    '''
    user = request.user
    
    if lists_type == 'bookmarks':
        posts = user.bookmarked_posts.select_related(
                                    'author', 'author__profile'
                                ).prefetch_related(
                                    'like_users', 'tags', 'bookmarks'
                                ).all() #(bookmarks__bookmark_by_id=request.user.id)
        
    elif lists_type == 'reading-history':
        posts = user.read_history_posts.select_related(
                                            'author', 'author__profile'
                                        ).prefetch_related(
                                            'like_users', 'tags', 'bookmarks'
                                        ).all()


    return render(request, 'blog/library.html', {
        'lists_type': lists_type,
        'posts': posts,
    })


@login_required
def clear_bookmarks(request):
    '''Clear all bookmaked posts if post request made 
    '''
    user = request.user
    if request.method == 'POST':
        user.bookmarked_posts.clear()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def clear_history(request):
    ''' This is to clear all read history posts by current user
    '''
    user = request.user
    if request.method == 'POST':
        user.read_history_posts.clear()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def my_stories(request, stories='drafts'):
    """This is to view list of Draft posts when stories for the owner user
        and Published posts of author
    """
    user = request.user
    draft_posts =  BlogPost.objects.filter(author=user).exclude(status='published')
    public_posts = BlogPost.all_published.filter(author=user)
    
    return render(request, "blog/my_stories.html", {
        "posts": public_posts if stories == 'published' else draft_posts,
        "stories": stories,
        # "draft_count": draft_posts.count(),
        # "public_count": public_posts.count(),
    })


@login_required
def stats(request):
    return HttpResponse("Your story stats coming soon!")

