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

WORKDIR /usr/src/app
COPY . .
RUN /usr/src/app/scripts/update_apt.sh
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv lock -r | grep -E '==|-i|-e' > requirements.txt
RUN pip install -r requirements.txt


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


EXPOSE 8080
RUN python manage.py collectstatic --noinput
ENTRYPOINT ["uwsgi", "uwsgi.ini"]
