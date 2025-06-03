#!/bin/sh
export OPENAI_API_KEY=$(cat "$OPENAI_API_KEY_FILE")
exec "$@"
