
from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory  

from ckeditor.widgets import CKEditorWidget       
from .models import BlogPost, UserProfile, Category, TaggedItem, Tag, Comment


# Create custom form
class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    
    # Remove all fields label
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, field in self.fields.items():
            # if field.label != "Featured image":
            field.label = ""
    
        
    class Meta:
        model = BlogPost
        
        fields = ("title", "subtitle", "content") # /*"featured_image", "featured_image_caption",
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control no-shadow fs-3", "placeholder": "Title"}),
            "subtitle": forms.TextInput(attrs={"class": "form-control no-shadow", "placeholder": "Subtitle"}),
            # "featured_image": forms.TextInput(attrs={"class": "form-control no-shadow", "type": "file", "placeholder": "choose"}),
            # "featured_image_caption": forms.TextInput(attrs={"class": "form-control no-shadow", "placeholder": "Featured img caption"}),
            "content": forms.Textarea(attrs={'class': 'form-control', })
            
        }


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for key, field in self.fields.items():
            field.label = ""
        

    class Meta:
        model = Comment

        fields = ("body",)
        widgets = {
            "body": forms.Textarea(attrs={'class': 'form-control rounded no-shadow txta-mod', "rows": 1, })
        }