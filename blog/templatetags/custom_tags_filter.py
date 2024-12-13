import re
import datetime 
import math

from django import template
from django.utils import timezone


register = template.Library()

# @register.filter(name="short_num")
def short_num(value):

  if value < 10e2:
    return value
  
  elif value >= 10e2 and value < 10e5:
    return str(round(value / 10e2, 1)) + "K"
  
  elif value >= 10e5 and value < 10e8:
    return str(round(value / 10e5, 1)) + 'M'

  else:
    return str(round(value / 10e8, 1)) + 'B'


@register.filter(name="readmins")
def read_time(safe_content):
  # regex = re.compile(r)
  words = re.findall(r'(\w+)\b', safe_content)

  readmin = round(len(words) / 250)
  return 1 if readmin < 1 else readmin


@register.filter(name='item_exists')
def item_exists(item, list):
  return item in list


@register.filter(name="my_timesince")
def my_timesince(time):
  date_type = {
    'year': 'yr',
    'month': 'm',
    'week': 'w',
    'day': 'd',
    'hour': 'h',
    'minute': 'm',
    'second': 's'
  }

  now = timezone.now()
  d_time = now - time

  if d_time.days < 1:
    d_time = d_time.seconds / 60 /  60
    if d_time >= 1:
      return str(math.ceil(d_time)) + date_type.get('hour')
    else:
      d_time = d_time * 60
      if d_time >= 60:
        return str(math.ceil(d_time)) + date_type.get('minute')
      else:
        return str(math.ceil(d_time)) + date_type.get('second')
  
  elif 1 <= d_time.days < 7:
    return str(d_time.days) + date_type.get('day')

  else:
    return time

# Register short_num filter
register.filter('shortnum', short_num)


# Create custom simple tags
@register.simple_tag(takes_context=True)
def share_on_x(context, post_abs_url, title=None):
  # Get request from context
  request = context.get('request')

  # Get Full url from any blog page
  get_full_url = request.build_absolute_uri(post_abs_url)

  return f"https://twitter.com/intent/tweet?text={title}&url={get_full_url}"


@register.simple_tag(takes_context=True)
def share_on_facebook(context, post_abs_url, title=None):
  # Get request from context
  request = context.get('request')

  # Get Full url from any blog page
  get_full_url = request.build_absolute_uri(post_abs_url)

  return f'https://www.facebook.com/sharer/sharer.php?u={get_full_url}&t={title}'


@register.simple_tag(takes_context=True)
def share_on_linkedin(context, post_abs_url, title=None):
  # Get request from context
  request = context.get('request')

  # Get Full url from any blog page
  get_full_url = request.build_absolute_uri(post_abs_url)

  return f'https://www.linkedin.com/shareArticle?mini=true&url={get_full_url}&title={title}'
