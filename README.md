# Asterisk Prometheus AMI Exporter
Asterisk Metrics Exporter using Asterisk Manager Interface - WORK IN PROGRESS!

## Running in docker
Like this:
```
docker build . -t ami_stats
docker run --rm -it --network=asterisk_default -e AMI_HOST=asterisk -e AMI_USER=test \
 -e AMI_SECRET=test -e PUSH_GATEWAY=pushgw ami_stats
```
Or if you run asterisk and prometheus / pushgateway with port forwarding try this:
```
docker run --rm -it --network=host -e AMI_USER=user -e AMI_SECRET=secret ami_stats
```
In this case default ENV values are used (AMI_HOST=localhost and PUSH_GATEWAY=localhost:9091)
