#!/bin/bash
# Start script for Render
# Starts Node.js TVM server in background, then runs the bot
echo "Starting TVM server..."
node tvm_server.js &
sleep 4
echo "Starting bot..."
python acki_bot.py bot $TELEGRAM_TOKEN
