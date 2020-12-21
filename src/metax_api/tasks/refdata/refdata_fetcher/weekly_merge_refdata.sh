#!/bin/bash
# Script to gather one week's daily reference data changes to master branch and tag it

echo --- Weekly repository upkeep started ---

REFDATA_REPO_PATH=/code/metax-refdata

if [ ! -d "$REFDATA_REPO_PATH" ]; then
  echo "Reference data repository directory $REFDATA_REPO_PATH DOES NOT exists."
  exit 1
fi

NOW=$( date '+%Y/%U' )
echo $NOW
NEW_BRANCH=Reference-data-weekly-$NOW

cd $REFDATA_REPO_PATH

git stash
git checkout master
git pull --prune

BRANCHES=$(git branch -a|grep Reference-data-changes)
echo "Branches to merge
$BRANCHES"

git checkout -b $NEW_BRANCH

if [ -z "$BRANCHES" ]; then
  echo No branches to merge
  exit 0
fi

# force merge every daily branch to master
for BRANCH in $BRANCHES
  do
    echo "Merging $BRANCH"
    if [[ $BRANCH == remotes/origin/Reference-data-changes* ]]
      then
        REMOTE="$(echo $BRANCH | sed 's!remotes/origin/!!g')"
        git fetch origin $REMOTE
        git merge -X theirs origin/$REMOTE -m "Weekly merge $NOW"
        git branch -D $REMOTE
        git push origin :$REMOTE
      else
        git merge -X theirs $BRANCH -m "Weekly merge $NOW"
        git branch -D $BRANCH
        git push origin :$BRANCH
    fi
  done

# create weekly tag with year/week
git push -u origin $NEW_BRANCH
git checkout master

echo --- Repository upkeep finished ---