import multiprocessing

#   bind - The socket to bind.
#
#   backlog - The number of pending connections. This refers
#       to the number of clients that can be waiting to be
#       served. Exceeding this number results in the client
#       getting an error when attempting to connect. It should
#       only affect servers under significant load.
#
#       Must be a positive integer. Generally set in the 64-2048
#       range.
#

bind = '127.0.0.1:8011'
backlog = 2048

#   workers - The number of worker processes that this server
#       should keep alive for handling requests.
#
#       A positive integer generally in the 2-4 x $(NUM_CORES)
#       range. You'll want to vary this a bit to find the best
#       for your particular application's work load.
#
#   worker_class - The type of workers to use. The default
#       async class should handle most 'normal' types of work
#       loads. You'll want to read http://gunicorn/deployment.hml
#       for information on when you might want to choose one
#       of the other worker classes.
#
#       An string referring to a 'gunicorn.workers' entry point
#       or a python path to a subclass of
#       gunicorn.workers.base.Worker. The default provided values
#       are:
#
#           egg:gunicorn#sync
#           egg:gunicorn#eventlet   - Requires eventlet >= 0.9.7
#           egg:gunicorn#gevent     - Requires gevent >= 0.12.2 (?)
#           egg:gunicorn#tornado    - Requires tornado >= 0.2
#
#   worker_connections - For the eventlet and gevent worker classes
#       this limits the maximum number of simultaneous clients that
#       a single process can handle.
#
#       A positive integer generally set to around 1000.
#
#   timeout - If a worker does not notify the master process in this
#       number of seconds it is killed and a new worker is spawned
#       to replace it.
#
#       Generally set to thirty seconds. Only set this noticeably
#       higher if you're sure of the repercussions for sync workers.
#       For the non sync workers it just means that the worker
#       process is still communicating and is not tied to the length
#       of time required to handle a single request.
#
#   keepalive - The number of seconds to wait for the next request
#       on a Keep-Alive HTTP connection.
#
#       A positive integer. Generally set in the 1-5 seconds range.

workers = multiprocessing.cpu_count() * 2 + 1
# einfach den namen ohne egg:gunicorn (oder die komplette django klasse): 'sync', 'eventlet', 'gevent', 'gunicorn.workers.ggevent.GeventWorker' 
worker_class = 'eventlet'
worker_connections = 1000
timeout = 30
keepalive = 2

#   debug - Turn on debugging in the server. This limits the number of
#       worker processes to 1 and changes some error handling that's
#       sent to clients.
#
#       True or False

debug = False
pidfile = '/var/www/env_projects/pymonit/gunicorn.pid'

#daemon = False
#umask = 0

#   loglevel - The granularity of log output
#
#       A string of "debug", "info", "warning", "error", "critical"
#
logfile = 'gunicorn.log'
loglevel = 'debug'