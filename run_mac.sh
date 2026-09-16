#!/bin/bash
# Script para rodar o jogo garantindo o uso do ambiente virtual (venv)
cd "$(dirname "$0")" || exit 1
echo "Iniciando Hand Pong..."

if [ -f "./.venv/bin/python3" ]; then
    ./.venv/bin/python3 main.py
elif [ -f "./venv/bin/python3" ]; then
    ./venv/bin/python3 main.py
else
    python3 main.py
fi
