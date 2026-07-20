# Stage 1 - Compile needed python dependencies
FROM python:3.12-slim-trixie AS backend-build

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
        pkg-config \
        build-essential \
        git \
        libpq-dev \
        # required for (log) routing support in uwsgi
        libpcre2-8-0 \
        libpcre2-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY ./requirements /app/requirements
RUN pip install pip "setuptools>=70.0.0"
RUN pip install -r requirements/production.txt


# Stage 2 - build frontend
FROM node:26-trixie-slim AS frontend-build

WORKDIR /app

COPY ./*.json /app/
RUN npm ci --legacy-peer-deps

COPY ./*.js /app/

COPY src/objects/scss/ /app/src/objects/scss/
COPY src/objects/js/ /app/src/objects/js/
RUN npm run build


# Stage 3 - Build docker image suitable for execution and deployment
FROM python:3.12-slim-trixie AS production

# Stage 3.1 - Set up the needed production dependencies
# install all the dependencies for GeoDjango
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
        postgresql-client \
        gdal-bin \
        gettext \
        libpcre2-8-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pip "setuptools>=70.0.0"

COPY --from=backend-build /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=backend-build /usr/local/bin/uwsgi /usr/local/bin/uwsgi
COPY --from=backend-build /usr/local/bin/celery /usr/local/bin/celery

# Stage 3.2 - Copy source code
WORKDIR /app
COPY ./bin/wait_for_db.sh /wait_for_db.sh
COPY ./bin/docker_start.sh /start.sh
COPY ./bin/celery_worker.sh /celery_worker.sh
COPY ./bin/celery_flower.sh /celery_flower.sh
COPY ./bin/check_celery_worker_liveness.py ./bin/
COPY ./bin/setup_configuration.sh /setup_configuration.sh
COPY ./bin/dump_data.sh /dump_data.sh
COPY ./bin/uwsgi.ini /
RUN mkdir /app/log /app/config /app/tmp

# copy frontend build statics
COPY --from=frontend-build /app/src/objects/static /app/src/objects/static
COPY --from=frontend-build /app/node_modules/@fortawesome/fontawesome-free/webfonts /app/node_modules/@fortawesome/fontawesome-free/webfonts

# copy source code
COPY ./src /app/src

RUN useradd -M -u 1000 user
RUN chown -R user /app

# drop privileges
USER user

ARG COMMIT_HASH
ARG RELEASE
ENV GIT_SHA=${COMMIT_HASH}
ENV RELEASE=${RELEASE}

ENV DJANGO_SETTINGS_MODULE=objects.conf.docker

ARG SECRET_KEY=dummy
ARG SITE_DOMAIN=dummy

# Run collectstatic, so the result is already included in the image
RUN python src/manage.py collectstatic --noinput

LABEL org.label-schema.vcs-ref=$COMMIT_HASH \
      org.label-schema.vcs-url="https://github.com/maykinmedia/open-object" \
      org.label-schema.version=$RELEASE \
      org.label-schema.name="Open Object"

EXPOSE 8000
CMD ["/start.sh"]
