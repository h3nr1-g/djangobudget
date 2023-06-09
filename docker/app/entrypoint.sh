#!/bin/bash
export DJANGO_SETTINGS_MODULE=djangobudget.settings.prod
export PYTHONUNBUFFERED=1

# run custom command if provided
if [ $# -gt 0 ]; then
  eval "$@"
fi

# wait for DB server to come up
db_rc=0
table_num=""
while [ -z "$table_num" ] && [ "$db_rc" -eq "0" ]; do
    echo "Try to check DB state ..."
    table_num=$(echo "SELECT COUNT(*) FROM information_schema.tables WHERE TABLE_SCHEMA ='$MYSQL_DATABASE';" |  mysql -h $MYSQL_HOST -u $MYSQL_USER --password="$MYSQL_PASSWORD" $MYSQL_DATABASE 2>/dev/null | tail -n 1)
    db_rc=$?
    if [ ! -z "$table_num" ] && [ "$db_rc" -eq "0" ]; then
        break
    fi
    echo "Could not connect to DB server. Try again in 3 second."
    sleep 3
done

sleep 3
python manage.py makemigrations budgets common users --noinput --no-color
python manage.py migrate --noinput --no-color

gunicorn \
  --daemon \
  --bind 127.0.0.1:8888 \
  --threads 2 \
  djangobudget.wsgi:application

nginx -g 'daemon off; master_process on;'
