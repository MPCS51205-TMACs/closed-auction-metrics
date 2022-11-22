#!/usr/bin/env bash
# Filename: build-all-images.sh

# stop script upon encountering the first error
# without closing terminal window
set -e


#####
# this script builds all images for the project from
# dockerfiles
#####

# RUN set-env-vars.sh first!

# need: location of docker file for the image you want to build
# need: a name for the image you are going to create

export MONGO_IMG_DOCKERFILE="$CLOSED_AUCTION_METRICS_DIR_PATH/mongodb/"
export MONGO_IMG_NAME="mongo-server"

export RABBITMQ_IMG_DOCKERFILE="$CLOSED_AUCTION_METRICS_DIR_PATH/rabbitmq/"
export RABBITMQ_IMG_NAME="rabbitmq-server"

export CLOSED_AUCTION_METRICS_IMG_DOCKERFILE="$CLOSED_AUCTION_METRICS_DIR_PATH/closed-auction-metrics/"
export CLOSED_AUCTION_METRICS_IMG_NAME="closed-auction-metrics"

echo
echo RUNNING SCRIPT TO BUILD PROJECT IMAGES...
echo SCRIPT_DIR=$SCRIPT_DIR
echo
echo MONGO_IMG_DOCKERFILE=$MONGO_IMG_DOCKERFILE
echo MONGO_IMG_NAME=$MONGO_IMG_NAME
echo
echo RABBITMQ_IMG_DOCKERFILE=$RABBITMQ_IMG_DOCKERFILE
echo RABBITMQ_IMG_NAME=$RABBITMQ_IMG_NAME
echo
echo CLOSED_AUCTION_METRICS_IMG_DOCKERFILE=$CLOSED_AUCTION_METRICS_IMG_DOCKERFILE
echo CLOSED_AUCTION_METRICS_IMG_NAME=$CLOSED_AUCTION_METRICS_IMG_NAME
echo

# we create each image from a docker file, using the docker command:
# 'docker build -t IMAGETAGNAME:VERSION PATHTODOCKERFILE'
# RABBIT MQ
echo "building RabbitMQ image ($RABBITMQ_IMG_NAME) from dockerfile..."
docker build -t "$RABBITMQ_IMG_NAME:latest" $RABBITMQ_IMG_DOCKERFILE

# Postgres SQL
echo "building Mongo image ($MONGO_IMG_NAME) from dockerfile..."
docker build -t "$MONGO_IMG_NAME:latest" $MONGO_IMG_DOCKERFILE

# RABBIT MQ
echo "building ClosedAuctionMetricsService ($CLOSED_AUCTION_METRICS_IMG_NAME) image from dockerfile..."
docker build -t "$CLOSED_AUCTION_METRICS_IMG_NAME:latest" $CLOSED_AUCTION_METRICS_IMG_DOCKERFILE

echo "done"