#!/usr/bin/env bash
set -e

for dir in libs/*; do
	(cd "$dir" && git clean -xdf)
done

git clean -xdf
