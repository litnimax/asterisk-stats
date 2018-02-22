# Asterisk Stats
Asterisk Metrics Exporter to StatsD
Rquirements:
* Prometheus
* StatsD exporter - https://github.com/prometheus/statsd_exporter

## Running in docker
Set variables to connect to Asterisk in .env file (see .env.example):
* AMI_USER
* AMI_SECRET
* AMI_HOST
* AMI_PORT
```
docker-compose up
```
