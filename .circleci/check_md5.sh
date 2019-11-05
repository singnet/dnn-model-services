#! /bin/bash

declare -a arr=("Dockerfile" "requirements.txt")
RET_VAL=0

for TARGET_FILE in "${arr[@]}"
do
    CURRENT_MD5=$(md5sum "${SERVICE_DIR}"/"${TARGET_FILE}")
    REMOTE_MD5=$(ssh -o "StrictHostKeyChecking no" "${SSH_USER}"@"${SSH_HOST}" docker exec "${PROD_TAG}""${DOCKER_CONTAINER_NAME}" md5sum "${TARGET_FILE}")

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
