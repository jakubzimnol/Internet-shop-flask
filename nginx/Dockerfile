FROM nginx:latest

ARG NGINX_CONFIG

RUN rm /etc/nginx/conf.d/*
COPY $NGINX_CONFIG /etc/nginx/conf.d/

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log
