FROM alpine:edge

RUN apk update \
        && apk --no-cache add dnsmasq

RUN mkdir -p /etc/default/
COPY dnsmasq.conf /etc/dnsmasq.conf
COPY dnsmasq.hosts /etc/dnsmasq.hosts

ENTRYPOINT dnsmasq --no-daemon --log-queries
