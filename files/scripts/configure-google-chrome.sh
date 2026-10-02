#!/usr/bin/env bash
set -euo pipefail

# Google's mutable-host maintenance recreates its DNF repo and imports RPM
# keys at runtime. Chrome is image-owned here; updates arrive through uupd.
# BlueBuild's built-in /opt handling keeps application content image-owned.
rpm -q google-chrome-stable
rm -f /etc/cron.daily/google-chrome /etc/yum.repos.d/google-chrome.repo
install -d /etc/default
printf 'repo_add_once="false"\n' > /etc/default/google-chrome
