#!/bin/bash
# Script to fetch reference data and organization data to version control

REFDATA_REPO_PATH=/code/metax-refdata

if [ ! -d "$REFDATA_REPO_PATH" ]; then
  echo "Reference data repository directory $REFDATA_REPO_PATH DOES NOT exists."
  exit 1
fi

NOW=$( date '+%Y%m%dT%H%M%S' )
NEW_BRANCH=Reference-data-changes-$NOW

# fetching reference data
cd /code/
python manage.py fetch_refdata

# checking changes
cd $REFDATA_REPO_PATH
CHANGES=$(git diff --name-only)

if [ -z "$CHANGES" ]; then
  echo "No changes in reference data. Exiting..."
  exit 2
fi

echo --- Name of new branch $NEW_BRANCH
echo --- Changes to be commited $CHANGES

# fetching reference data
git checkout -b $NEW_BRANCH
git add .
git commit -m "Updated reference data"
git push -u origin $NEW_BRANCH
git checkout master