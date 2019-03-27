#!/usr/bin/env bash
# shellcheck disable=SC2059
rm /etc/apt/sources.list
printf "deb http://archive.debian.org/debian/ jessie-backports main\n" |  tee -a /etc/apt/sources.list
printf "deb-src http://archive.debian.org/debian/ jessie-backports main\n" |  tee -a /etc/apt/sources.list
printf "Acquire::Check-Valid-Until false;\n" |  tee -a /etc/apt/apt.conf.d/10-nocheckvalid
printf 'Package: *\nPin: origin "archive.debian.org"\nPin-Priority: 500\n' |  tee -a /etc/apt/preferences.d/10-archive-pin
apt-get update