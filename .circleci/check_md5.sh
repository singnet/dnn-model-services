#! /bin/bash

declare -a arr=("${SERVICE_FOLDER}"/Dockerfile "${SERVICE_FOLDER}"/requirements.txt)
RET_VAL=0

for TARGET_FILE in "${arr[@]}"
do
    CURRENT_MD5=$(md5sum "${TARGET_FILE}")
    REMOTE_MD5=$(ssh -o "StrictHostKeyChecking no" "${SSH_USER}"@"${SSH_HOST}" docker exec "${PROD_TAG}""${DOCKER_CONTAINER_NAME}" md5sum "${TARGET_FILE}")

    if [ "${CURRENT_MD5}" != "${REMOTE_MD5}" ]
        then
        # "${TARGET_FILE} has changed!"
        ((RET_VAL+=1))
    fi
done

echo ${RET_VAL}
