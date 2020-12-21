#!/bin/bash
# Script to reindex all reference data and organization data.

echo --- Daily reindexing started ---

NOW=$( date '+%Y%m%dT%H%M%S' )
echo $NOW

REFDATA_REPO_PATH=/code/metax-refdata

if [ ! -d "$REFDATA_REPO_PATH" ]; then
  echo "Reference data repository directory $REFDATA_REPO_PATH DOES NOT exists."
  exit 1
fi

cd $REFDATA_REPO_PATH
git checkout master
git pull --prune
cd /code/
python manage.py index_refdata

echo --- Reindexing finished ---