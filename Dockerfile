FROM python:3.6.4
LABEL MAINTAINER="Collins Macharia <collins.macharia@andela.com>"
LABEL application="artbackend"


ARG SECRET_KEY='secret key'
ARG DJANGO_SETTINGS_MODULE='settings.prod'
ARG HOST_IP

# Prevent dpkg errors
ENV TERM=xterm-256color  \
    SECRET_KEY=${SECRET_KEY} \
    DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

ENV HOST_IP=${HOST_IP}
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    vim \
    cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . .
RUN pip install pipenv
RUN pipenv lock -r | grep -E '==|-i' > requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8080
RUN python manage.py collectstatic --noinput
ENTRYPOINT ["gunicorn", "art.wsgi"]
