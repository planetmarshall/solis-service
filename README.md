# Solis / Ginlong Inverter Service

This Python package implements a service that interprets messages from a Solis PV Inverter
monitoring device and can persist them to a local database

## Installing as a service

To install as a service, I use [supervisor](http://supervisord.org/).

    sudo pip install .
    sudo pip install supervisor
    adduser solis
    sudo mkdir -p /var/log/solis
    sudo chown -R solis:solis /var/log/solis

Create a `supervisord.conf` if you have not already done so and edit. For example,

    [program:solis_ginsong_server]
    command=/usr/local/bin/solis_ginsong_server
    user=solis
    stdout_logfile=/var/log/solis/solis.log
    stderr_logfile=/var/log/solis/solis_error.log


