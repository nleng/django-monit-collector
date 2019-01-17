# django-monit-collector

This is a django project, which collects data from <a href="https://mmonit.com/monit/" target="_blank">monit</a> instances on one or multiple servers, stores them and visualizes them using <a href="http://getbootstrap.com/" target="_blank">bootstrap</a> and the javascript library <a href="http://dygraphs.com/" target="_blank">dygraphs</a>. Example website: http://monitcollector.cfsme-network.de

There is a very similar app for the server monitoring tool <a href="https://github.com/Supervisor/supervisor" target="_blank">supervisor</a> called <a href="https://github.com/nleng/djangovisor" target="_blank">djangovisor</a>.


### Features
- Collects and parses monit xml data from one or multiple servers. 
- Stores the data for a given time period. 
- Displays it in pretty graphs. 
- Start/stop/restart buttons for processes.
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
import monitcollector.urls as m_urls

url(r'^monitcollector/', include(m_urls)),
```
Create/sync the database and create a superuser (you need to login to access the monit-collector dashboard):
```
python manage.py syncdb
```
Collect static files:
```
python manage.py collectstatic
```
With correct webserver configurating the app should then be available at http://mydomain.com/monitcollector/. 

In your monitrc file add this line to send data to the collector.
```
set mmonit http://mydomain.com/monitcollector/collector
```
If you want to enable the start/stop buttons (optional), the monit http daemon must be available, in monitrc (you can also)
```
set httpd port 2812
  allow myuser:mypassword
```
If you don't want to allow access from everywhere add "allow ip.address..." with the ip address of the server, where monitcollector is installed. 
The user and password have to be set in the settings.py:
```
ENABLE_BUTTONS = True
MONIT_USER = youruser
MONIT_PASSWORD = yourpassword
MONIT_PORT = 2812
```
You don't have to specify the port if you use the default port 2812. Also, the port must not be blocked by the firewall, e.g. 
```
ufw allow 2812
```

You can also monitor this app with monit itself. Not using the privided script lead to error in my case.
```
check process monitcollector with pidfile /path/to/pid/gunicorn.pid
  start program = "/project/path/gunicorn.sh start"
  stop program = "/project/path/gunicorn.sh stop"
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

