#!/bin/bash
set -e

cd $(dirname $0)
rm -rf out
PIPENV_MAX_DEPTH=6 pipenv run python -m ros_translator -t=typescript -o=out ros_translator_test_msgs
echo 'test build'
tsc --noEmit
echo 'ok'
ts-node -T $(npx which jasmine) "$@"
