#!/bin/bash
# Script to fetch reference data and organization data to version control

cd /usr/local/metax/refdata_indexer
source /usr/local/metax/pyenv/bin/activate

if [ "$USER" != "metax-user" ]; then
    echo "Run this as metax-user"
    exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "Give exactly one parameter to the script: path to the reference data repository."
  exit 2
fi

if [ ! -d "$1" ]; then
  echo "Directory $1 DOES NOT exists."
  exit 3
fi

REPO_PATH=$1
NOW=$( date '+%Y%m%dT%H%M%S' )
NEW_BRANCH=Reference-data-changes-$NOW

# fetching reference data
source /usr/local/metax/pyenv/bin/activate
cd /usr/local/metax/refdata_writer
python fetch_data.py $REPO_PATH

# checking changes
cd $REPO_PATH
CHANGES=$(git diff --name-only)

if [ -z "$CHANGES" ]; then
  echo "No changes in reference data. Exiting..."
  exit 4
fi

# fetching reference data
git checkout -b $NEW_BRANCH
git add .
git commit -m "Updated reference data"
git push -u origin $NEW_BRANCH
git checkout master