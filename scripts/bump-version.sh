#!/usr/bin/env bash

# bump semver of module

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo 'bump to new version'

version=`cat ${DIR}/../version.txt`
versions=`git tag --list`

echo 'current version' ${version}

#increase patch

target_version=$1

# major, minor, patch
case ${target_version} in
    major)
    major_inc=1
    minor_inc=0
    patch_inc=0
    echo "major update"
    shift
    ;;
    minor)
    major_inc=0
    minor_inc=1
    patch_inc=0
    echo "minor update"
    shift
    ;;
    *)
    major_inc=0
    minor_inc=0
    patch_inc=1
    target_version=patch
    echo "patch"
    ;;
esac

echo ${target_version}

version_array=( ${version//./ } )
major_version=${version_array[0]}
minor_version=${version_array[1]}
patch_version=${version_array[2]}
next_version="$((${major_version}+${major_inc})).$((${minor_version}+${minor_inc})).$((${patch_version}+${patch_inc}))"

echo "next version ${next_version}"

echo ${next_version} > ${DIR}/../version.txt
echo 'updated version.txt'

if [[ ${versions} == *${next_version}* ]]; then
   echo 'already has this version'
   exit 1
fi

# TODO: update CHANGELOG
# github_changelog_generator

# don't need to deploy yet
# ${DIR}/deploy.sh

git commit -am "bump to ${next_version}"
git tag ${next_version}
git push
git push --tag
