#!/bin/bash
# Terminal recovery script for SenseTop
# Run this if your terminal gets stuck after a crash: bash scripts/reset_terminal.sh

echo "Resetting terminal state..."

# Reset terminal to sane state
reset

# Alternative: use tput to reset
# tput reset

echo "Terminal reset complete!"
echo "If cursor is still invisible, try: tput cnorm"
echo "If colors are wrong, try: tput sgr0"
