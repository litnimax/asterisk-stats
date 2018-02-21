# Asterisk Stats
Asterisk Metrics Exporter to StatsD
Rquirements:
* Prometheus
* StatsD exporter - https://github.com/prometheus/statsd_exporter

## Running in docker
Like this:
```
docker build . -t ami_stats
docker run --rm -it --network=asterisk_default -e AMI_HOST=asterisk -e AMI_USER=test \
 -e AMI_SECRET=test -e STATSD_HOST=localhost:9125 ami_stats
```
Or if you run asterisk and prometheus & prometheus statsd_exporter port forwarding try this:
```
docker run --rm -it --network=host -e AMI_USER=user -e AMI_SECRET=secret ami_stats
```
In this case default ENV values are used (AMI_HOST=localhost and PUSH_GATEWAY=localhost:9091)

## Docker compose
```
  prometheus:
    image: prom/prometheus:v2.1.0
    container_name: prometheus
    volumes:
      - ./prometheus/:/etc/prometheus/
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention=200h'
      - '--web.enable-lifecycle'
    #restart: unless-stopped
    expose:
      - 9090
    ports:
      - 127.0.0.1:9090:9090
      
  statsd_exporter:
    container_name: statsd_exporter
    image: prom/statsd-exporter
    expose:
      # web port for prometheus pulls
      - 9102
    ports:
      - "9125:9125"
      - "9125:9125/udp"
```

Prometheus config
```
scrape_configs:
  - job_name: 'statsd_exporter'
    scrape_interval: 10s
    static_configs:
      - targets: ['statsd_exporter:9102']
```
