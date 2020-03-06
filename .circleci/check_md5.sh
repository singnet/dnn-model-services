#! /bin/bash

FILES_LIST=$1
# Removing possible white spaces from FILES_LIST
FILES_LIST=$(echo "${FILES_LIST}" | tr -d ' ')
# Creating an array of FILE_PATHS
IFS=','
read -ra ARR <<< "$FILES_LIST"

RET_VAL=0

cd "$SERVICE_DIR" || exit

for TARGET_FILE in "${ARR[@]}"
do
  CURRENT_MD5=$(md5sum "${TARGET_FILE}")
  REMOTE_MD5=$(ssh -o "StrictHostKeyChecking no" "${SSH_USER}"@"${SSH_HOST}" docker exec "${PROD_TAG}""${DOCKER_CONTAINER}" md5sum "${TARGET_FILE}")

  # Getting only the hash
  CURRENT_MD5=$(echo "${CURRENT_MD5}" | awk '{ print $1 }')
  REMOTE_MD5=$(echo "${REMOTE_MD5}" | awk '{ print $1 }')

  if [ "${CURRENT_MD5}" != "${REMOTE_MD5}" ]
      then
      # "${TARGET_FILE} has changed!"
      ((RET_VAL+=1))
  fi
done

echo ${RET_VAL}