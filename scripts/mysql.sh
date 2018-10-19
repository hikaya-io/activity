#!/bin/bash

# USAGE: sh mysql.sh -u USERNAME -r -f BACKUP_FILE_NAME.sql
#               -u = your username for the database
#               -r = resets the database (drops existing one, creates a new one)
#               -f = restores this backup file
#               -e = points to the python executable so that migrations command can be run
#               -b = backs up the database of the $host
#               -h = Specified which host's db to backup
# If this file is located where the Django's manage.py file is located then
# it will run the migration command as well.

# Database credentials
user=
password=
host="localhost"
db_name="tola_activity"


backup_path="$HOME/sqlbackups"
date=$(date +"%d-%b-%Y")

restore=0
backup=0
file2restore=
resetdb=
pythonexe=
deleteoldbackups=

# Number of days to keep backups
keep_backups_for=30 #days

while [ "$1" != "" ]; do
    case $1 in
        -u | --user )       shift
                            user=$1
                            ;;
        -p | --password)    shift
                            password=$1
                            ;;
        -h | --host )       shift
                            host=$1
                            ;;
        -b | --backup )     backup=1
                            ;;
        -f | --file )       shift
                            file2restore=$1
                            ;;
        -e | --exe )        shift
                            pythonexe=$1
                            ;;
        -d | --del )        shift
                            deleteoldbackups=1
                            ;;
        -r | --reset )      resetdb=1
                            ;;
        -h | --help )       usage
                            exit
                            ;;
        * )                 usage
                            exit 1
    esac
    shift
done

# prints a horizontal line
function hr(){
  printf '=%.0s' {1..80}
  printf "\n"
}

# delete old backups of type sql.gz
function delete_old_backups() {
  echo "Deleting $backup_path/*.sql.gz older than $keep_backups_for days"
  find $backup_path -type f -name "*.sql.gz" -mtime +$keep_backups_for -exec rm {} \;
  # delete old files of type .sql
  find $backup_path -type f -name "*.sql" -mtime +$keep_backups_for -exec rm {} \;
  # find $backup_path/* -mtime +$keep_backups_for -exec rm {} \;
}

if [ $backup -eq 1 ]
then
    echo "backing db $backup"
    #mysqldump --user=$user --password=$password --host=$host $db_name > $backup_path/$db_name-$date.sql
    mysqldump --user=$user --password --host=$host $db_name > $backup_path/$host-$db_name-$date.sql
else
    echo "NOT backingup db at $host"
fi
sleep 0.5

# if resetdb variable is not empty
if [ ! -z "$resetdb" ]
then
    echo "dropping db at localhost"
    mysql -h localhost -u $user -p mysql --password <<< "drop database $db_name"
    echo "creating db at localhost"
    mysql -h localhost -u $user -p mysql --password <<< "create database $db_name"
fi

sleep 1

# if file2restore variable is not empty
if [ ! -z "$file2restore" ]
then
    echo "Restoring $file2restore"
    # restore the database
    mysql -h localhost -u $user -p "$db_name" < "$backup_path/$file2restore"
fi

sleep 0.5

# if file exists
if [ -f 'manage.py' ]
then
    # if pythonexe variable is not empty
    if [ ! -z "$pythonexe" ]
    then
        $pythonexe manage.py migrate
    fi
fi

# Delete files older than 30 days
if [ ! -z "$deleteoldbackups" ]
then
    hr;
    delete_old_backups;
fi

