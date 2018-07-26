#!/usr/bin/env bash
set -eo pipefail

DEPLOY_SCRIPT_PATH="${HOME}/deploy"

curl -o $DEPLOY_SCRIPT_PATH https://raw.githubusercontent.com/AndelaOSP/bash-helper-modules/master/k8s/deploy

source $DEPLOY_SCRIPT_PATH
CURRENTIPS=""
DOCKER_REGISTRY=gcr.io
GCLOUD_SERVICE_KEY_NAME=gcloud-service-key.json
ALLOWED_DEPLOY_ENVIRONMENTS=('staging', 'production')

require 'PRODUCTION_GOOGLE_COMPUTE_ZONE' $PRODUCTION_GOOGLE_COMPUTE_ZONE
require 'STAGING_GOOGLE_COMPUTE_ZONE' $STAGING_GOOGLE_COMPUTE_ZONE
require 'STAGING_CLUSTER_NAME' $STAGING_CLUSTER_NAME
require 'PRODUCTION_CLUSTER_NAME' $PRODUCTION_CLUSTER_NAME
require 'PROJECT_NAME' $PROJECT_NAME
require 'GOOGLE_PROJECT_ID' $GOOGLE_PROJECT_ID
require 'DOCKER_REGISTRY' $DOCKER_REGISTRY
require 'GCLOUD_SERVICE_KEY' $GCLOUD_SERVICE_KEY
getHosts(){ 
    echo "============> geting hosts "
    if [ "$CIRCLE_BRANCH" == 'master' ]; then
      CURRENTIPS="$(gcloud compute instances list --project bench-projects | grep  gke-bench-production-default-pool | awk -v ORS=, '{if ($4) print $4}' | sed 's/,$//')"
    else
      CURRENTIPS="$(gcloud compute instances list --project bench-projects | grep  gke-bench-staging-default-pool | awk -v ORS=, '{if ($4) print $4}' | sed 's/,$//')"
    fi
}

buildAndTagDockerImages() {
    require "IMAGE_NAME" $IMAGE_NAME
    info "Building image with tag $IMAGE_NAME ....."
    docker build --build-arg HOST_IP=$CURRENTIPS -t $IMAGE_NAME $@
}


BRANCH_NAME=$CIRCLE_BRANCH
# set the deployment environment
setEnvironment $BRANCH_NAME
# ensure its an allowed deployment environment
isAllowedDeployEnvironment $ENVIRONMENT
# get K8s deployment name

getDeploymentName DEPLOYMENT_NAME

# Set image image tag and name
IMAGE_TAG=$(getImageTag $(getCommitHash))
IMAGE_NAME=$(getImageName)

main() {
    installGoogleCloudSdk
    authWithServiceAccount
    configureGoogleCloudSdk
    getHosts
    loginToContainerRegistry _json_key
    buildAndTagDockerImages .
    publishDockerImage
    logoutContainerRegistry $DOCKER_REGISTRY
    deployToKubernetesCluster backend
}

main