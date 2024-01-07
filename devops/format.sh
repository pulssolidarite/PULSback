#!/bin/bash

# Set the color variables
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color


printf "\n${BLUE}        +------------------+\n"
printf "        |    Formatting    |\n"
printf "        +------------------+${NC}\n\n"

. venv/bin/activate
black .