#!/bin/bash

# current Git branch
branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')
devBranch=develop

# v1.0.0, v1.5.2, etc.
lastTag=$(git describe --tags $(git rev-list --tags --max-count=1))

git reset --hard origin/$devBranch
git pull origin $devBranch
if [ -z "$lastTag" ] ; then
    tagMessage=$(git log $devBranch --no-merges --pretty=format:"%s")
    lastTag=v0.9.9
else
    tagMessage=$(git log $lastTag..$devBranch --no-merges --pretty=format:"%s")
fi

# Increment tag number
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

git tag -a $versionLabel -m "$tagMessage"

echo "Release Notes:"
echo $tagMessage

# push including created tag
git push origin $versionLabel
