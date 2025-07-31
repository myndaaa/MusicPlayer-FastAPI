#!/bin/bash

# script to mirror a personal GitHub repository to a Monstarlab repository
# better  to run it on desktop/intenrsip dir rather than repo dir (scary!!)
set -e

cleanup() {
  echo "Cleaning up temp mirror git file"
  cd ..
  rm -rf temp-mirror.git
}
trap cleanup EXIT

echo "Cloning personal repo"
git clone --mirror https://github.com/myndaaa/MusicPlayer-FastAPI.git temp-mirror.git

cd temp-mirror.git

echo "Setting Monstarlab repo as destination"
git remote set-url origin https://github.com/monstar-lab-bd/internship-musicstreamer-fastapi-flutter.git

echo "Pushing mirror to Monstarlab repo"
git push --mirror
echo "mirror successful"
