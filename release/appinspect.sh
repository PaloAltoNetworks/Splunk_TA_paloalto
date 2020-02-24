#!/bin/bash

# MUST BE RUN FROM APP ROOT

NAME=Splunk_TA_paloalto
VERSION=`grep -o '^version = [0-9a-z.-]*' default/app.conf | awk '{print $3}'`
if [ "${TRAVIS}" == "true" ]; then
    BUILD=${TRAVIS_BUILD_NUMBER}
    BRANCH=${TRAVIS_BRANCH}
else
    BUILD="local"
    BRANCH=`git rev-parse --abbrev-ref HEAD`
fi
echo "AppInspect ${NAME} ${VERSION} build ${BUILD} for SplunkBase"

curl -X POST \
  --url "https://appinspect.splunk.com/v1/app/validate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Cache-Control: no-cache" \
  -F "included_tags=cloud" \
  -F app_package=${NAME}-${VERSION}-${BRANCH}-${BUILD}.tgz
