FROM python:3.6

LABEL MAINTAINER="Collins Macharia <collins.macharia@andela.com>"
LABEL application="hofbackend"


ARG SECRET_KEY='secret key'
ARG DJANGO_SETTINGS_MODULE='settings.prod'
# ARG HOST_IP

# Prevent dpkg errors
ENV TERM=xterm-256color  \
    SECRET_KEY=${SECRET_KEY} \
    DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

# ENV HOST_IPS=${HOST_IP}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    vim \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8080
ENTRYPOINT ["gunicorn", "art.wsgi"]
