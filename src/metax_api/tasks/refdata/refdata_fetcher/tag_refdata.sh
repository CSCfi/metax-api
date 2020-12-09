#!/bin/bash
# Script to gather one week's daily reference data changes to master branch and tag it

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

NOW=$( date '+%Y/%U' )
REPO_PATH=$1

cd $REPO_PATH

BRANCHES=$(git branch -a|grep "^Reference-data-changes")
echo "Branches to merge $BRANCHES"

git checkout master
git pull

for BRANCH in $BRANCHES
    do
        echo "Merging $BRANCHh"
        git merge -X theirs $BRANCH -m "Weekly merge $NOW"
        git branch -D $BRANCH
        git push origin :$BRANCH
    done

git tag -a $NOW -m "Weekly changes from $NOW"
git push origin $NOW
git push
