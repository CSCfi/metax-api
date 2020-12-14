#!/bin/bash
# Script to gather one week's daily reference data changes to master branch and tag it

REFDATA_REPO_PATH=/code/metax-refdata

if [ ! -d "$REFDATA_REPO_PATH" ]; then
  echo "Reference data repository directory $REFDATA_REPO_PATH DOES NOT exists."
  exit 1
fi

NOW=$( date '+%Y/%U' )

cd $REFDATA_REPO_PATH

BRANCHES=$(git branch -a|grep "^Reference-data-changes")
echo "Branches to merge $BRANCHES"

git checkout master
git pull

for BRANCH in $BRANCHES
    do
        echo "Merging $BRANCH"
        git merge -X theirs $BRANCH -m "Weekly merge $NOW"
        git branch -D $BRANCH
        git push origin :$BRANCH
    done

git tag -a $NOW -m "Weekly changes from $NOW"
git push origin $NOW
git push
