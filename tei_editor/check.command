#!/bin/bash

cd "$(dirname "$0")" || {
    printf 'ERROR: I could not open the TEI editor folder.\n'
    IFS= read -r -p 'Press Return to close this window. ' _
    exit 1
}

if [ ! -x ".venv/bin/python" ]; then
    printf 'ERROR: The app setup is missing. Double-click start.command once, then try this checker again.\n'
    printf '\nPress Return to close this window. '
    IFS= read -r _
    exit 1
fi

printf 'Checking data/transcription.xml...\n\n'
.venv/bin/python check_tei.py
CHECK_STATUS=$?

printf '\nPress Return to close this window. '
IFS= read -r _
exit "$CHECK_STATUS"
