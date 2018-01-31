#!/bin/bash

loc="`dirname \"$0\"`"

if [ ${#} == 1 ]
then
	psql -U tony -d postgres -c "REVOKE CONNECT ON DATABASE ${1} FROM public;"
	psql -U tony -d postgres -c "select pg_terminate_backend(procpid) from pg_stat_activity where datname='${1}' and procpid != pg_backend_pid();"
	psql -U tony -d postgres -c "drop database ${1}"
	psql -U tony -d postgres -c "create database ${1}"
	psql -U tony -d "${1}" -f "${loc}/createtables.sql"
else
	echo Please specify a database name
fi
