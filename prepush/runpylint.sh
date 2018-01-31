PROJ=$1
RCFILE=$PROJ/prepush/.pylintrc

PYTHONPATH=${PYTHONPATH}:${PROJ}/webapp:${PROJ}/webapp/pages:${PROJ}/webapp/lib:${PROJ}/webapp/data \
    pylint --rcfile=${RCFILE} \
    ${PROJ}/webapp/
