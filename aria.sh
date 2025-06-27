#!/bin/bash

aria2c --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all=true \
--rpc-listen-port=6800 --dir=/downloads --max-connection-per-server=10 --rpc-secret="" &

sleep 3
python3 bot.py
