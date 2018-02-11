# Asterisk Prometheus AMI Exporter
Asterisk Metrics Exporter using Asterisk Manager Interface - WORK IN PROGRESS!

## Running in docker
Like this:
```
docker build . -t ami_stats
docker run --rm -it --network=asterisk_default -e AMI_HOST=asterisk -e AMI_USER=test \
 -e AMI_SECRET=test -e PUSH_GATEWAY=pushgw ami_stats
```
