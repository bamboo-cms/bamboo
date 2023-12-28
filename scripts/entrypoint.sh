#!/bin/bash

set -eo pipefail

command="$1"

case "$command" in
  start)
    echo "Migrating the database"
    flask create-tables
    flask db upgrade
    echo "Starting the app"
    exec gunicorn app:app
    ;;
  *)
    exec flask "$@"
esac
