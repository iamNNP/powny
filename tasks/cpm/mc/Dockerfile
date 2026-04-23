FROM ubuntu:20.04 AS ubuntu
FROM pwn.red/jail

COPY --from=ubuntu / /srv

COPY app /srv/app

ENV JAIL_PORT=11778
ENV JAIL_TIME=120

RUN chmod +x /srv/app/mc && ln -s /app/mc /srv/app/run