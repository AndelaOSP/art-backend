#!/bin/bash

# current Git branch
branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

# v1.0.0, v1.5.2, etc.
lastTag=$(git describe --tags $(git rev-list --tags --max-count=1))

if [ -z "$lastTag" ] ; then
    lastTag=v0.9.9
fi

removedV=${lastTag//v}
part1=$(cut -d'.' -f1 <<<"$removedV")
part2=$(cut -d'.' -f2 <<<"$removedV")
part3=$(cut -d'.' -f3 <<<"$removedV")

part3=$((part3 + 1))

if (( $part3 > 9 )) ; then
    part3=0
    part2=$((part2 + 1))
fi

if (( $part2 > 9 )) ; then
    part2=0
    part1=$((part1 + 1))
fi
versionLabel=v$part1.$part2.$part3

echo "New version: $versionLabel"

echo "===> establish branch and tag name variables"
devBranch=develop
masterBranch=master

echo "===> fetch latest origin"
git fetch origin
git fetch --tags

echo "===> pull latest master"
git checkout $masterBranch
git reset --hard origin/$(git_current_branch)
git pull origin $(git_current_branch)

echo "===> commit version number increment"
git commit -am "Release version $versionLabel"

# merge the new version number back into develop
echo "===> merge master to develop"
git checkout $devBranch
git reset --hard origin/$(git_current_branch)
git pull origin $(git_current_branch)

# create tag for new version from -master
tagMessage=$(git log --all --grep='(#' -i $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%h %s")
git tag -a $versionLabel -m $tagMessage

git merge --no-ff $masterBranch

# push including all tags
git push origin --tags
