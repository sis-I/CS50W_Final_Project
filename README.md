# Introduction
This is a final project for the completing of cs50 Web Programming with Python and JavaScript course. My wife, who is both a writer and an editor, and I were discussing potential ideas for this final project. We realized that there are currently no dedicated blogging platforms in Ethiopia for individuals wishing to share long-form articles, short stories, personal experiences, and similar content. Most people resort to using Facebook for writing and sharing, which limits their readership due to the nature of social media. Consequently, we decided to create a dedicated blogging website where users can read and share their thoughts in the comments section and have the option to share their posts on other social media platforms if they choose.

This project is developed using `HTML`, `CSS`, `Bootstrap`, `JavaScript` on front-end and `Django`, `Python`, and `SQLite3` for the back-end.

This project is built to be Mobile responsive.

## Distinctiveness and Complexity
### Distinctiveness
-  This project, a blogging web app, is distinct from any other projects in CS50 Web that we have completed before. It is a blogging platform that allows registered users, whether amateur or professional authors, to write articles, share personal experiences, create tutorials, and tell stories for the world to see. The app features a tagging system and many additional functionalities that enhance the user experience and facilitate content discovery.

### Complexity 
This project is complex that includes:
- __User Authentication__: Users can sign in, sign out, sign up, and utilize Django's built-in password reset system.

- __Multiple Models and Forms__: It features various models, forms, and HTML templates for writing, viewing, updating, and deleting blog posts and other contents.

- __Key Features__:

    + A custom tagging system for filtering posts by categories and suggesting content based on user interests.
    + Post sharing, liking, commenting (with options to view, delete, and like comments), and replying to comments.
    + Bookmarking functionality, storing read history, and a robust search feature.

+ __Advanced Search__: The search functionality includes users, post titles, and tags/categories, using JavaScript for front-end suggestions in a modal box and displaying results on a separate page.
+ __Hierarchical Categories__: Categories are displayed in a hierarchical order with lists of blog posts under each category/tag.

+ __Recommendations__: The app suggests trending blog posts and tags based on users' interests, previous likes, reading history, and followings.
+ __Tag Management__: New tags are slugified using JavaScript upon creation.
+ __Custom Decorators__: A decorator function checks if a user is the author of a specific post.
+ __Image Management__: Users can upload, view, and change feature images for their posts.
+ __User Profiles__: Users can create and edit profiles, including uploading, changing, or deleting avatars.


## Files and Folders Contained

### Django built-in Files and Folders

#### Under `capstone` folder
- `settings.py`: responsible of different configurations and app registration
- `urls.py`: urls of the project apps will be registered here

####  Database
- `db.sqlite3`: Sqlite3 database of the project

#### Base Templates
 - `base.html`: for common html navbars, nav menu, search bar, right side offcanvas box. and registers all frontend dependencies like css, bootstrap and common JavaScript applictions
 - `footer.html`: html for footer section 
 
#### Base Static Folder
 static folder holds all css, JavaScript, and media files

 - css > `main.css`: holds all css styles in the whole project
 - js > `dashboard.js`: holds JavaScript content only used in dashboard page.
 - js > `util.js`: holds JavaScript functions, expressions, api requests/responses used by any page
 - `media > images > avatar`: all user avatars will be stored here.
- `media > blog > featured_pics`: all featured images of a blog post will be stored here

#### Accounts App
+ `accounts`: this is a folder containing 'accounts' app files.

__Under `templates > accounts`__: accounts app HTML files

- `signup.html`: User registration page
- `login.html`: This component displays the LOGIN view, which includes input fields for the username and password, along with a submit button for logging in. If the user is not registered, there is a button that redirects them to the signup page. Additionally, if the user has forgotten their password, there is a button available to assist for password reset.
- `logout.html`:  used for logout page, with link to redirect to login
- `reset_password.html`: reset password intiation page
- `reset_password_done.html`: page reset password was initiated and notify user password reset verification link sent.
- `password_reset_email.html`: view password reset verification link
- `reset_password_confirm.html`: reset password page for changing and confiming new password,
- `reset_password_complete.html`: a notifying page that password reset has been successfully completed.

__Python files__
- `__init__.py`, `app.py`, & `tests.py`: not modified
- `admin.py`: registering User and TaggedItems models
- `models.py`: User models and other models created, to then be migrated to the database table
- `urls.py`: This file contains the URLs for the Accounts app, where they are registered.
- `views.py`: This file contains all the logic necessary to handle requests and render the appropriate responses for Login, Logout, Sign Up, and Password Reset functionalities.

 #### Blog App
+ `blog/`: this is a folder containing 'blog' app files.

__Under `templates > blog/`__: containes blog app templates files

- `index.html`: This is used to render home page for users who are not signed in.
- `dashboard.html`: This file displays the dashboard view after the user signed in, which includes lists of posts under For You, Following, and categories the user interested in. 
- `category_list.html`: This file renders a list of categories in hierarchical order, displaying both parent and child categories.
- `create_or_edit_post.html`:  This file is used to render the post writing and editing page, featuring the necessary fields for publication. It allows users to create their own tags or select from available tags. Users can choose to save their created posts as drafts or publish them. Additionally, this file is utilized for editing posts that have already been published by the author.

- `detail_post.html`: This file is responsible for displaying individual posts and includes various functionalities such as liking, commenting, and replying to comments. It also allows the author to delete or update their post, share the post, bookmark it, and more.

- `follower_list.html`: This file displays a list of users who are followers of a specific user. 
- `following_list.html`: This file displays a list of users who are followed by a specific user.
- `library.html`:  This file showcases both the bookmarked posts and the list of posts that have been read. It is viewed when the 'Library' item is clicked in the off-canvas menu on the right side by the current signed in user.  Only user can see their own bookmarked and read stories. The use clear all bookmarks or delete individual bookmarked post and clear all posts under read history,
- `my_stories.html`: This file displays both draft posts and the list of posts that have been published by owner user. It is viewed when the 'Stories' item is clicked in the off-canvas menu.

- `post_list.html`:   This file serves as a reusable list of posts that can be utilized across different pages and for various purposes. It will be used on the homepage, in the library, in stories, and more. This template can be included in other template files using the Django '{% include %}' tag.

- `profile.html`: This file displays users profile page, it showcases a list of public posts authored by a specific user. It is viewed when the 'Profile' item is clicked in the off-canvas menu.

- `profile_lists.html`: This file displays a list of posts that have been bookmarked by requesting user who is singed in. It is viewed when the 'Lists' seciton is clicked in the profile page.

- `profile_about.html`: This file displays all about the user's profile. User's avatar, bio, and date of birth viewd. Requesting user can update, delete thier own profile.

- `search_results.html`: This file displays search results of users, posts, and topics.

- `tagged_post_list.html`: This file displays list of similar posts under a specified tag.

- `user_row.html`: This file serves as a reusable individual user that can be utilized across different pages for list of users. 

__Python files__
- `__init__.py`, `app.py`, & `tests.py`: not modified
- `admin.py`: registering BlogPost, Category, Tag,UserProfile and TaggedItems models to the admin web page. 
- `forms.py`: This file is used to create forms for the BlogPost and Comment models, specifying the necessary fields and customizing their appearance.

- `models.py`: This file contains the definitions for the BlogPost, UserProfile, Comment, TaggedItem, Category, Tag, BlogBookmark, and BlogHistory models. Once migrated, these models will be created as tables in the database.

- `urls.py`: This file contains URL paths for the Blog app to view page responses and handle responses to API requests, where they are registered.

- `views.py`:  This file contains all the logic necessary to handle requests and render the appropriate responses for the Blog app. It includes views for the index/home page, dashboard, create or edit post page, detail post page, library page, profile page, my stories page, following and followers pages, categories list page, tagged posts list under a specific tag view page, and search result view page. Additionally, it manages API requests such as deleting stories, providing search result suggestions, toggling likes on posts and comments, following or unfollowing users and topics, creating or deleting comments and replies, adding or removing bookmarks, recording read post history, and clearing all bookmarks and histories. The file also includes complex database queries.

Under `custom_decorators/` folder

- `decorators.py`: This file contains a decorator that checks if a user is the owner of a specific post. If the user is not the owner, it returns a bad request response. This decorator is utilized in various view functions within the application.

 `templatetags/`: has custom templates filter and tags
    
- `custom_tags_filter.py`:  This file includes various custom template filters, such as displaying large numbers in a shortened format, calculating the read time of a post, checking if an item exists in a list, and providing a custom timesince filter. Additionally, it contains custom tags that can be used for sharing posts on different social media platforms.

- README.md: This file provides this documentaion that is being written on.

### How to Run This Application

.   Clone repository

    >> git clone https://github.com/me50/sis-I.git/web50/projects/2020/x/capstone
    
.   Change directory to capstone

    >> cd capstone

.   Install all neccessary dependencies

    >> pip install -r requirements.txt

.   Initiate all created models as migration files and then apply these migrations to the database corresponding tables

    >> python manage.py makemigrations
    >> python manage.py migrate`
.   Create web sites admin by 

    >> django-admin createsuperuser

.   Start the server 

    >> python manage.py runserver

### Closing Thoughts
It was an incredible experience taking this course. I am truly grateful for the knowledge and insights gained throughout the journey. I would like to extend my heartfelt thanks to our instructor [Brian Yu](brian@cs.harvard.edu) for his guidance, support, and dedication. Their expertise and encouragement made a significant difference in our learning experience. Thank you, Brian Yu and Thank you to all the team in CS50.

ሰላም!!
