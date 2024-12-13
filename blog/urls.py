from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'blog'

urlpatterns = [
    path("", views.index, name="home"),

    # path("blog/posts", views.posts_list, name="posts-list"),
    path("blog/<int:year>/<int:month>/<int:day>/<slug:post_slug>",
                                views.post_detail, name="post-detail"),
    path("new-story", views.write_or_edit_story, name="new_story"),
    path("edit/<int:post_id>", views.write_or_edit_story, name="edit_story"),
    path("edit/<int:post_id>/<str:status>", views.write_or_edit_story, name="edit_public_story"),
    path("delete/<int:post_id>", views.delete_story, name="delete_story"),

    # Search result views 
     path('search/<str:query_on>', views.search_results_view, name='search-results'), 

    # User Profile page
    path("u/<str:username>", views.profile_view, name="user-profile"),
    path("u/<str:username>/lists", views.profile_lists_view, name="user-profile-lists"),

    path("u/<str:username>/about", views.profile_about_view, name="user-profile-about"),
    # Use singlepage using APIview
    path("u/<str:username>/about/create-or-edit", views.create_or_edit_profile, name="create-or-edit-profile"),

    # User Following and Follower List 
    path("u/<str:username>/followings", views.followings_view, name="user-followings"),
    path("u/<str:username>/followers", views.followers_view, name="user-followers"),

    # Library Your lists (reading-list), reading history
    path("me/lists/<str:lists_type>", views.library, name="library"),
    # path("me/lists/reading-history", views.reading_history, name="reading-history"),
    path("me/lists/bookmarks/clear-bookmarks", views.clear_bookmarks, name="clear-bookmarks"),
    # path("me/lists/bookmarks/<int:post_id>/delete", views.delete_bookmark, name="delete-bookmark"),
    path("me/lists/reading-history/clear-all", views.clear_history, name="clear-history"),
    # Stories
    path("me/stories/<str:stories>", views.my_stories, name="stories"),
    # path("me/stories/published", views.published_stories, name="published-stories"),
    # path("me/stories/submitted", views.submitted_stories, name="submitted-stories"),

    # Stroy statistics
    path("me/stats", views.stats, name="stats"),

    # List of Categories
    path('topics/', views.category_list, name="category-list"),
    
    # Posts categorized/tagged
    path('tag/<str:slug>', views.tagged_posts, name='tagged-stories'),

    # API view 
    path('search', views.search_modal_result, name='search'), 
    path('follow/<str:username>', views.follow_or_unfollow, name='follow-user'),
    path('like-post/<int:post_id>', views.like_or_unlike_post, name='like-post'),
    path('publish_comment', views.publish_comment, name="publish-comment"),
    path('delete_comment/<int:comment_id>', views.delete_comment, name="delete-comment"),
    # path('edit_comment/<int:comment_id>', views.edit_comment, name="edit-comment"),
    path('like-comment/<int:comment_id>', views.toggle_like_comment, name="toggle-like-comment"),
    path("reply/<int:comment_id>", views.reply_comment, name="reply-comment"),
    path('follow-topic/<str:tag_slug>', views.toggle_topic_follow, name='follow_topic'),
    path('bookmark-post/<int:post_id>', views.add_or_remove_bookmark, name='bookmark_post'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

