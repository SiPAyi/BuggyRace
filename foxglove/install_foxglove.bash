#!/bin/bash
set -e

echo -e "\e[2;32mInstalling latest foxglove studio\e[0m"
echo -e "\e[2;32mMaking sure system is up to date.\e[0m"
sudo apt-get update
sudo apt-get dist-upgrade -y
sudo apt-get install jq ca-certificates curl gnupg -y

if [ -f /snap/bin/foxglove-studio ]; then
  echo -e "\e[31mFound snap installed foxglove studio, removing for debian based install.\e[0m"
  sudo snap remove foxglove-studio
fi

if [ -f /usr/bin/foxglove-studio ]; then
  echo -e "\e[2;32mFound already debian installed foxglove studio.\e[0m"
else
  echo -e "\e[2;32mDownloading and installing latest foxglove studio.\e[0m"
  mkdir -p /tmp/foxglove-install
  cd /tmp/foxglove-install
  curl -L   -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    https://api.github.com/repos/foxglove/studio/releases/latest \
    | jq '.assets[0].browser_download_url' | xargs wget
  sudo apt install ./foxglove-studio-*.deb
  cd ~/cognipilot
  rm -rf /tmp/foxglove-install
fi


echo -e "\e[2;32m\nFoxglove installer is complete, open foxglove-studio through app launcher or command line.\e[0m"

