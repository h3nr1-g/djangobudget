#!/bin/bash
export PYTHONUNBUFFERED=1
set -o pipefail


function run_app () {
    echo "Starting djangobudget application ..."
    gunicorn \
      --daemon \
      --bind 127.0.0.1:8888 \
      --threads 2 \
      djangobudget.wsgi:application
    nginx -g 'daemon off; master_process on;'
}


function init_db () {
    echo "Database $MYSQL_DATABASE empty. Run initial migrations ..."
    python manage.py migrate
    echo "Load languages ..."
    for file in $(ls common/res/lang); do
        python manage.py loadlang common/res/lang/$file
    done
    echo "Create admin account"
    python manage.py createsuperuser --noinput
    echo "Create sample budget"
    python manage.py loaddata budgets/res/sample.json
}


function wait_for_db () {
  while true; do
      echo "Try to check DB state ..."
      table_num=$(echo "SELECT COUNT(*) FROM information_schema.tables WHERE TABLE_SCHEMA ='$MYSQL_DATABASE';" |  mysql -h $MYSQL_HOST -u $MYSQL_USER --password="$MYSQL_PASSWORD" $MYSQL_DATABASE 2>/dev/null | tail -n 1)
      db_rc=$?
      if [ "$db_rc" -eq "0" ]; then
          if [ "$table_num" -eq "0" ]; then
              init_db
          fi
          break
      fi
      echo "Could not connect to DB server. Try again in 3 second."
      sleep 3
  done
}


# run custom command if provided
if [ $# -gt 0 ]; then
    eval "$@"
    exit $?
fi

wait_for_db
run_app
