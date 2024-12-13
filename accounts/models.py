from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation


# Create your models here.
class User(AbstractUser):
    
    followings = models.ManyToManyField('self', through='UserRelation', 
                                        symmetrical=False, related_name="followers")
    
    # roles = models.ManyToManyField('UserRole', default='regular')
    interests = GenericRelation('blog.TaggedItem',
                                object_id_field='object_id',
                                content_type_field='content_type',
                                related_query_name='topic_followers')
   
    REQUIRED_FIELDS = ['interests']


class UserRole(models.Model):
    ADMIN = 'admin'
    STAFF = 'staff'
    REGULAR = 'regular'
    AUTHOR = 'author'
    EDITOR = 'editor'
    PUBLICTION_OWNER = 'pub_owner'

    role = models.CharField(max_length=10, choices=[(ADMIN, 'Admin'), 
                                                    (STAFF, 'Staff'),
                                                    (REGULAR, 'Regular'),
                                                    (AUTHOR, 'Author'),
                                                    (EDITOR, 'Editor'),
                                                    (PUBLICTION_OWNER, 'pub_owner')
                                                    ])
    
# Intermediary Model
class UserRelation(models.Model):

    user_follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_users")
    followed_user= models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_users")

    created_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"<{self.user_follower.username}> follows {self.followed_user.username}"
    
