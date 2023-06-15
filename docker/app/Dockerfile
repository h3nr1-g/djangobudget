FROM python:3.11-bullseye

RUN apt-get update -y && apt-get install -y \
    curl \
    python3-dev \
    python3-pip \
    mariadb-client \
    nginx

COPY . /djangobudget
WORKDIR /djangobudget

RUN pip3 install -r requirements.txt
RUN pip3 install  mysqlclient gunicorn

RUN sed -i 's|djangobudget.settings.dev|djangobudget.settings.prod|g' manage.py

RUN python manage.py collectstatic --noinput --no-color

RUN rm -rf /etc/nginx/sites-*
RUN mv docker/app/nginx.conf /etc/nginx/nginx.conf

ENTRYPOINT /djangobudget/docker/app/entrypoint.sh