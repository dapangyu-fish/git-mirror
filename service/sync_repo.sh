#!/bin/bash

upstream_url=$(git config --get remote.upstream.url)
if [ $? -eq 1 ]; then
  origin_url=$(git config --get remote.origin.url)
  echo "use origin_url $origin_url as upstream_url"
  git remote add upstream "$origin_url"
else
  echo "using upstream_url $upstream_url"  
fi

git fetch upstream

refs=($(git for-each-ref --format='%(refname)' refs/remotes/upstream/))
for element in "${refs[@]}"; do
  suffix="${element#refs/remotes/upstream/}"
  git update-ref refs/heads/$suffix upstream/$suffix
done

git lfs fetch --all

git repack -a
git gc
