# django-pymonit

This is a django project, which collects data from <a href="https://mmonit.com/monit/" target="_blank">monit</a> instances on one or multiple servers, stores them and visualizes them using <a href="http://getbootstrap.com/" target="_blank">bootstrap</a> and the javascript library <a href="http://dygraphs.com/" target="_blank">dygraphs</a>. Example website: http://monitcollector.cfs-me-research.net/monitcollector/server/5/

### Features
- Collects and parses monit xml data from one or multiple servers. 
- Stores the data for a given time period. 
- Displays it in pretty graphs. 
- Start/stop/restart buttons for processes (only for the server where monitcollector is installed).
- Status tables and graphs are refreshing automatically via ajax.
- Processes are automatically removed when they stop sending data (removed from monitrc). Servers can be deleted manually.

### Installation

Just install it via pip:
```
pip install django-monit-collector
```
Or clone the repository if you want to modify the code:
```
git clone https://github.com/nleng/django-monit-collector
```
Add 'monitcollector' to your installed apps in settings.py:
```
INSTALLED_APPS = [
    'monitcollector',
    # ...
]
```
If you want to you can change the default values in your settings.py:
```
# should be the same as set in the monitrc file e.g. "set daemon 60"
MONIT_UPDATE_PERIOD = 60
# maximum days to store data, only correct, if MONIT_UPDATE_PERIOD is set correctly
MAXIMUM_STORE_DAYS = 7
```
Include monitcollector in your url.py:
```
url(r'^monitcollector/', include('monitcollector.urls')),
```
In your monitrc file add this line to send data to the collector.
```
set mmonit http://mydomain.com/monitcollector/collector
```

You can also monitor this app with monit itself. It is important to write the full path to everything.
```
check process monitcollector with pidfile /path/to/pid/gunicorn.pid
  start program = "/virtualenv_path/bin/python /virtualenv_path/bin/gunicorn -c /project/path/gunicorn.conf.py /project/path/wsgi:application"
  stop program = "/usr/bin/pkill -f '/virtualenv_path/bin/python /virtualenv_path/bin/gunicorn -c /project/path/gunicorn.conf.py /project/path/wsgi:application'"
  if failed host 127.0.0.1 port 8011 protocol http then restart
  if 5 restarts within 5 cycles then alert
```
Then you should have the same port and pid path in your gunicorn.conf
```
bind = '127.0.0.1:8011'
...
pidfile = '/path/to/pid/gunicorn.pid' 
```

### License
BSD License.

