#!/bin/bash
APP_NAME="public-image-crop-server"
sudo docker rm $APP_NAME -f || echo "failed to remove existing public-image-crop-server"
id=$(sudo docker run -dit --restart='always' \
--name $APP_NAME \
-p 9375:9375 \
$APP_NAME)
echo "ID = $id"
sudo docker logs -f "$id"