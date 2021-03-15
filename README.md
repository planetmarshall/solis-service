# Solis / Ginlong Inverter Service

![Build and Run](https://github.com/planetmarshall/solis-service/actions/workflows/build.yml/badge.svg)

This Python package implements a service that interprets messages from a Solis PV Inverter
monitoring device and can persist them to a local database

## Configuration

See the example file in `conf`.

## Installing as a service

To install as a service, I use [supervisor](http://supervisord.org/).

    sudo pip install .
    sudo pip install supervisor
    adduser solis
    sudo mkdir -p /var/log/solis
    sudo chown -R solis:solis /var/log/solis

Create a `supervisord.conf`, if you have not already done so and edit. See the example in
the `conf` folder.

Run supervisor

    sudo supervisord -c conf/supervisord.conf
    supervisorctl -c conf/supervisord.conf status