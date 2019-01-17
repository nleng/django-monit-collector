from django import template
from django.utils import timezone
import time
from django.conf import settings
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

# does nothing at the moment!
@register.filter
def status_str(status, monitor):
    # if monitor == 0 and status not in ['starting...', 'stopping...', 'restarting...', 'disable monitoring...', 'enable monitoring...']:
        # return "Not monitored"
    return status

@register.filter
def status_class(status, monitor):
    # has to be first
    # if monitor == 0 and status not in ['starting...', 'stopping...', 'restarting...', 'disable monitoring...', 'enable monitoring...']:
        # return 'blue'
    if status == 'running':
        return 'green'
    if status in ['starting...', 'stopping...', 'restarting...']:
        return 'yellow'
    # else return error color
    return 'red'

@register.filter
def in_MB(value):
    if not isinstance(value, (int, basestring)):
        return ""
    return str(round(float(value)/1.e3, 1))+" MB"

@register.filter
def in_GB(value):
    if not isinstance(value, (int, basestring)):
        return ""
    return str(round(float(value)/1.e6, 1))+" GB"

@register.filter
def percent(value):
    if not isinstance(value, (float, basestring)):
        return ""
    return str(round(value, 1))+"%"


