#!/bin/bash
echo "Starting TVM server (bee_sdk)..."
node tvm_server.js &
sleep 5
echo "Starting Acki Nacki bot..."
python acki_bot.py bot $TELEGRAM_TOKEN
