#!/bin/bash

unset KUBECONFIG

cd .. && cd .. &&  docker build -f docker/Dockerfile.latest \
             -t chenbe/chatgpt-on-wechat .

docker tag chenbe/chatgpt-on-wechat chenbe/chatgpt-on-wechat:$(date +%y%m%d)