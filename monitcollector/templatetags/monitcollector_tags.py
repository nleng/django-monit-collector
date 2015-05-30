from django import template
from django.utils import timezone
import time
import settings
register = template.Library()

try:
    monit_update_period = settings.MONIT_UPDATE_PERIOD
except:
    monit_update_period = 60

@register.filter
def timestamp_to_date(timestamp):
    if not isinstance(timestamp, int):
        return ""
    return timezone.datetime.fromtimestamp(timestamp)

@register.filter
def time_class(timestamp):
    if not isinstance(timestamp, int):
        return ""
    if int(time.time()) > int(timestamp) + 3*monit_update_period:
        return "danger"
    return ""

@register.filter
def time_str(uptime):
    """ converts uptime in seconds to a time string """
    if not isinstance(uptime, int):
        return ""
    mins = (uptime/60) % 60
    hours = (uptime/60/60) % 24
    days = (uptime/24/60/60) % 365
    years = uptime/365/24/60/60
    if years == 0:
      if days == 0:
        if hours == 0:
          return "%sm" % mins
        return "%sh %sm" % (hours, mins)
      return "%sd %sh %sm" % (days, hours, mins)
    return "%sy %sd %sh %sm" % (years, days, hours, mins)

@register.filter
def status_str(status, monitor):
    if monitor == 0 and status not in ['starting...', 'stopping...', 'restarting...', 'disable monitoring...', 'enable monitoring...']:
        return "Not monitored"
    return status

@register.filter
def status_class(status, monitor):
    # has to be first
    if monitor == 0 and status not in ['starting...', 'stopping...', 'restarting...', 'disable monitoring...', 'enable monitoring...']:
        return 'blue'
    if status == 'running':
        return 'green'
    if status in ['starting...', 'stopping...', 'restarting...', 'disable monitoring...', 'enable monitoring...']:
        return 'yellow'
    # else return error color
    return 'red'

@register.filter
def last_item(item_list_str):
  if not isinstance(item_list_str, basestring):
    return ""
  item_list = item_list_str.strip('[]').split()
  if len(item_list) <1:
    return ""
  return item_list[-1]

@register.filter
def in_MB(value):
    # if not isinstance(value, float) and not isinstance(value, basestring):
    if value == "":
        return ""
    return str(round(float(value)/1.e3, 1))+" MB"

@register.filter
def in_GB(value):
    if value == "":
        return ""
    return str(round(float(value)/1.e6, 1))+" GB"

@register.filter
def procent(value):
    if value == "":
        return ""
    return str(value)+"%"



