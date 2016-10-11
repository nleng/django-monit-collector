#!/bin/bash
command="/virtualenv/path/bin/python /virtualenv/path/bin/gunicorn -c /project/path/gunicorn.conf.py --chdir /project/path wsgi:application"
pidfile=/project/patho/gunicorn.pid
logfile=/dev/null
errorlog=/project/path/gunicorn.log

if [ -f $pidfile ] ; then
	pid=`cat $pidfile`
fi

case "$1" in
'start')
		if [ -f $pidfile ] ; then
				if test `ps -e | grep -c $pid` = 1; then
						echo "already running with PID: $pid"
				else
						echo "starting gunicorn"
						exec $command  1> $errorlog 2> $logfile &
				fi
		else
				echo "starting gunicorn"
				exec $command  1> $errorlog 2> $logfile &
		fi
		;;
'stop')
		if [ -f $pidfile ] ; then
				echo "stopping gunicorn"
				# kill master process, never mind, just kill all
				# kill $pid
				pkill -f "$command"
		else
				echo "No pidfile found!"
				# kill all workers directly, if something wired happend to the pidfile
				pkill -f "$command"
		fi
		;;

'restart')
		$0 stop
		sleep 2
		$0 start
		;;

*)
		echo "usage: $0 { start | stop | restart }"
		;;
esac
exit 0