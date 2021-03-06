ARG BUILDFRONTENDFROM=node:14.15.1-buster
ARG SERVERFROM=python:3.9.0-buster

####################
# BUILDER FRONTEND #
####################

FROM ${BUILDFRONTENDFROM} as builder-frontend
ARG DOCKER_TAG
ADD frontend/package.json /frontend/
ADD frontend/package-lock.json /frontend/
WORKDIR /frontend
RUN npm install
ADD frontend /frontend
ENV REACT_APP_VERSION=$DOCKER_TAG
#ENV NODE_ENV=development
#ENV REACT_APP_VERSION=dev-in-docker
RUN npm run build -- --profile

##################
# BUILDER WHEELS #
##################

#FROM ${SERVERFROM} as builder-wheels

# set work directory
#WORKDIR /usr/src/app

# set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
#RUN apk update && apk add \
#    build-base \
#    ca-certificates \
#    musl-dev \
#    postgresql-dev \
#    python3-dev \
#    libffi-dev \
#    openldap-dev \
#    git \
#    xmlsec-dev \
#    libxml2-dev \
#    libxslt-dev
#RUN apt update && apt -y install \
#    build-essential \
#    ca-certificates \
#    musl-dev \
#    libpq-dev \
#    python3-dev \
#    libffi-dev \
#    libldap-dev \
#    git \
#    libsasl2-dev \
#    libxmlsec1-dev \
#    libxml2-dev \
#    libxslt-dev

#COPY guacozy_server/requirements*.txt ./
#RUN pip install --upgrade pip && \
#    pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements-full.txt

#########
# FINAL #
#########

FROM ${SERVERFROM}

#COPY --from=builder-wheels /usr/src/app/wheels /wheels

# install dependencies
#RUN apk update && apk add --no-cache \
#      bash \
#      libpq \
#      ca-certificates \
#      openssl \
#      memcached \
#      nginx \
#      supervisor \
#      xmlsec
RUN apt update && apt -y install \
      bash \
      libpq-dev \
      libldap2-dev \
      libsasl2-dev \
      ca-certificates \
      openssl \
      memcached \
      nginx \
      supervisor \
      xmlsec1 \
      libxml2-dev \
      libxmlsec1-dev \
      libxmlsec1-openssl 

# Inject built wheels and install them
#COPY --from=builder-wheels /usr/src/app/wheels /wheels
#RUN pip install --upgrade pip && \
#    pip install --no-cache /wheels/*

COPY guacozy_server/requirements-* /tmp/

RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements-full.txt

# Inject django app
COPY guacozy_server  /app

# Inject built frontend
COPY --from=builder-frontend /frontend/build /frontend

# Inject docker specific configuration
COPY docker /tmp/docker

# Distribute configuration files and prepare dirs for pidfiles
RUN mkdir -p /run/nginx && \
    cd /tmp/docker && \
    mv entrypoint.sh /entrypoint.sh && \
    chmod +x /entrypoint.sh && \
    mv nginx-default.conf /etc/nginx/conf.d/default.conf && \
    mkdir -p /etc/supervisor.d/ && \
    mv /tmp/docker/supervisor-app.ini /etc/supervisor.d/ && \
    mv /tmp/docker/supervisord.conf /etc/supervisord.conf && \
    # create /app/.env if doesn't exists for less noise from django-environ
    touch /app/.env

ENTRYPOINT ["/entrypoint.sh"]

# Change to app dir so entrypoint.sh can run ./manage.py and other things localy to django
WORKDIR /app

CMD ["supervisord", "-n"]
EXPOSE 80
EXPOSE 443
