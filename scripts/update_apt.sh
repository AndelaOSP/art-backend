#!/usr/bin/env bash
# shellcheck disable=SC2059
set -eo pipefail

rm /etc/apt/sources.list
echo "deb http://archive.debian.org/debian/ jessie-backports main" |  tee -a /etc/apt/sources.list
echo "deb-src http://archive.debian.org/debian/ jessie-backports main" |  tee -a /etc/apt/sources.list
echo "Acquire::Check-Valid-Until false;" |  tee -a /etc/apt/apt.conf.d/10-nocheckvalid
echo 'Package: *\nPin: origin "archive.debian.org"\nPin-Priority: 500' |  tee -a /etc/apt/preferences.d/10-archive-pin
apt-get update