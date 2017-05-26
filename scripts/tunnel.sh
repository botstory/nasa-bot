#!/usr/bin/env bash

ngrok http $(docker-machine ip $(docker-machine active)):${1:-$(APP-PORT)}
