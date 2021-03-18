# Solis / Ginlong Inverter Service

![Build and Run](https://github.com/planetmarshall/solis-service/actions/workflows/build.yml/badge.svg)

This Python package implements a service that interprets messages from a Solis PV Inverter
monitoring device and can persist them to various destinations

## Configuration

See the example file in `conf`.

### Persistence Clients

Currently [InfluxDb](https://www.influxdata.com/) is supported. Persistence clients are encapsulated such that
adding new ones should be straightforward. See the configuration file for details.

## Installing as a service

To install as a service, I use [supervisor](http://supervisord.org/).

    sudo pip install . supervisor
    adduser solis
    sudo mkdir -p /var/log/solis
    sudo chown -R solis:solis /var/log/solis

Create a `supervisord.conf`, if you have not already done so and edit. See the example in
the `conf` folder.

Run supervisor

    sudo supervisord -c conf/supervisord.conf
    supervisorctl -c conf/supervisord.conf status
    supervisorctl -c conf/supervisord.conf tail solis_service
