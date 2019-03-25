#!/usr/bin/env bash

working_dir='/var/lib/luka-cakechat-internal/'

dirs=('nn_models' 'tensorboard')

for path in "${dirs[@]}"; do
   sudo mkdir -p $working_dir$path
done

sudo chown -R "$USER" $working_dir
