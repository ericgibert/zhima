#!/usr/bin/env bash
# to be executed in the same durectory as zhima.py i.e. the executable part of the project
CWD=$(dirname $(readlink -f $BASH_SOURCE))
_IP=$(hostname -I | awk '{print $1}')
if [ -n $_IP ]; then
_IP=10.0.10.148
fi
rc=0
PID=$(cat $CWD/zhima.pid)
HTTP_PID=$(cat $CWD/http_view.pid)
# See how we were called.
case "$1" in
start)
    rm /home/pi/zhima/Private/sessions/sess*
    export WORKON_HOME=$HOME/.virtualenvs
    source $WORKON_HOME/zhima/bin/activate

    sudo pigpiod

    cd $CWD
    python3 http_view.py -b $_IP > $CWD/../Private/http_view.log 2>&1 &
    python3 zhima.py -b $_IP > $CWD/../Private/zhima.log 2>&1 &
    echo http://$_IP:8080
    ;;
stop)
    kill -9 $PID
    kill -9 $HTTP_PID
    ;;
status)
    echo "Current IP:" $_IP
    echo "Zhima pid:" $PID
    ps -fp $PID
    echo "HTTP view pid:" $HTTP_PID
    ps -fp $HTTP_PID
    ;;
restart|reload|force-reload)
    $0 stop
    $0 start
    rc=$?
    ;;
reboot)
    $0 stop
    sudo reboot
    ;;
*)
    echo $"Usage: $0 {start|stop|status|restart|reload|force-reload}"
    exit 2
esac

exit $rc
