FROM ubuntu:20.04 AS ubuntu
FROM pwn.red/jail

COPY --from=ubuntu / /srv

COPY app /srv/app

ENV JAIL_PORT=11777
ENV JAIL_TIME=120

RUN chmod +x /srv/app/jiro && ln -s /app/jiro /srv/app/run