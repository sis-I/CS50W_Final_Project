from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from accounts.models import User


# from django.conf import settings

''' User Profile '''
class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE,
							  related_name="profile", primary_key=True)
	avatar = models.ImageField(upload_to="images/avatar/", null=True, blank=True) # default="placeholder.png"
	date_of_birth = models.DateField(null=True, blank=True)
	bio = models.CharField(max_length=255, blank=True, null=True)
	
	
	def serialize(self):
		return {
			"id": self.user.id,
			"username": self.user.username,
			"date_of_birth": self.date_of_birth,
			"avatar": self.avatar.url if self.avatar else None,
			"bio": self.bio,
		}

	def __str__(self):
	    return f"{self.user.username}'s profile."
	

'''BlogPost Manager'''
class PublishedManager(models.Manager):
	def get_queryset(self):
		 return super().get_queryset().filter(status="published")

# CKEditor's RichTextField
from ckeditor.fields import RichTextField

class BlogPost(models.Model):
	POST_STATUS = (
		("draft", (
			("draft_unsubmitted", "Draft"),
			("draft_submitted", "Submitted"),
			("received", "Received"),
			("editor_assigned", "Editor assigned"),
			("editing", "Editing"),
			("rejected", "Rejected"),
			("accepted", "Accepted"),
		)),
		("published", "Published"),
	)
	
	
	title = models.CharField(max_length=255)
	subtitle = models.CharField(max_length=255, null=True, blank=True)
	slug = models.SlugField(max_length=255, unique_for_date="published_on", allow_unicode=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_posts")
	featured_image = models.ImageField(upload_to="images/blog/featured_pics", null=True, blank=True)
	featured_image_caption = models.CharField(max_length=255, null=True, blank=True)

	content = RichTextField(null=True, blank=True)
	#   role = models.CharField(max_length=2, choices=ROLE_CHOICES)
 
	status = models.CharField(max_length=20, choices=POST_STATUS, default="draft_unsubmitted")
	published_on = models.DateTimeField(null=True, blank=True)

	bookmarks = models.ManyToManyField(User, through='BlogBookmark', 
										related_name='bookmarked_posts', default=None, blank=True)
	
	reading_history = models.ManyToManyField(User, through='BlogHistory', related_name="read_history_posts",
										  blank=True)
	
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True) # get date for every change to the post and status of the post
		
	# Managers
	objects = models.Manager()
	all_published = PublishedManager()

	# User Likes
	like_users = models.ManyToManyField(User, blank=True, related_name="liked_posts")
	
	# TaggedItem for reverse query
	tags = GenericRelation("TaggedItem", related_query_name='similar_posts')

	
	class Meta:
		ordering = ('-published_on',)


	def __str__(self):
		return self.title
	
	
	def save(self, *args, **kwargs):
		if self.status == 'published' and not self.published_on:
			self.published_on = timezone.now()
		
		# Slugify
		if not self.slug:
			self.slug = slugify(self.title, allow_unicode=True)

		super().save(*args, **kwargs)
	
	
	def get_absolute_url(self):
			return reverse("blog:post-detail", args=(
												self.pub_year,
												self.pub_month,
												self.pub_day,
												self.slug
											))
	
	
	@property
	def pub_year(self):
		return self.published_on.year
	

	@property
	def pub_month(self):
		return self.published_on.month
	

	@property
	def pub_day(self):
		return self.published_on.day


# Tag Model	
class Tag(models.Model):
	name = models.CharField(max_length=100, unique=True)
	slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):

		# Use built in django slugify for tag slug
		if not self.slug:
			self.slug = slugify(self.name, allow_unicode=True)

		super().save(*args, **kwargs)
	
	def serialize(self):
		return {
			# 'id': self.id,
			'slug': self.slug,
			'name': self.name
		}
	
	class Meta:
		verbose_name = "tag"
		verbose_name_plural = 'tags'


class Category(Tag):
	# name = models.CharField(max_length=100) #  default="Uncategorized")
	parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, blank=True, null=True,
								related_name="children")
	# slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)
	
	class Meta:
		# unique_together = ('parent', 'slug',)
		# constraints = [
		# 	models.UniqueConstraint(fields=('parent','slug'), name="unique_category"),
		# ]
		verbose_name = 'category'
		verbose_name_plural = "categories"


	def __str__(self):
		p = self.parent
				
		cat_heirarchy = [self.name]
		while p is not None:
			cat_heirarchy.append(p.name) # insert(0, p.name) will be more expensive
			p = p.parent

		return  ' > '.join(cat_heirarchy[::-1])


class TaggedItem(models.Model):
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()

	content_obj = GenericForeignKey("content_type", "object_id")

	def __str__(self):
		return self.tag.name
	
	class Meta:
		indexes = [models.Index(fields=["content_type", "object_id"])]


# Comments on the Post
class Comment(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
	post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
	body = models.TextField()

	parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,
														related_name="replies")

	created_on = models.DateTimeField(auto_now_add=True)
	modified_on = models.DateTimeField(auto_now=True)

	like_users = models.ManyToManyField(User, blank=True, related_name="liked_comments")

	active = models.BooleanField(default=False)

	def __str__(self):

		return f"comment_id{self.id} on {self.post} by {self.author}"


class BlogBookmark(models.Model):
	# name = models.CharField(max_length=250, blank=True, default="Reading List")
	# slug = models.SlugField(max_length=250, blank=True, unique=True)
	# description = models.CharField(max_length=250, null=True, blank=True)
	bookmark_by = models.ForeignKey(User, on_delete=models.CASCADE)
	bookmark_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)

	created_on = models.DateTimeField(auto_now_add=True)

	# status = models.CharField(max_length=20, 
	# 								choices=(('private', 'Private'), ('public', 'Public'),), default='private')

	def __str__(self):
		return f'Post: {self.bookmark_post.id} bookmarked by user {self.bookmark_by}' 

	class Meta:
		ordering = ('-created_on', )
		unique_together = ('bookmark_by', 'bookmark_post',)


class BlogHistory(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)

	created_on = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'BlogHistory_id: {self.id} by user {self.user}'
