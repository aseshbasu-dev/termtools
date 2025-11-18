# TermTools Logs

This directory contains log files for TermTools sessions.

## Log File Location

**Production Mode** (installed in `C:\Program Files\BasusTools\TermTools\`):

- Logs are **always** created in: `C:\Program Files\BasusTools\TermTools\core\data\logs\`
- Regardless of which directory you run TermTools from (e.g., right-click in D:\songs)

**Development Mode** (running from source code directory):

- Logs are created in the local `core/data/logs/` directory
- This ensures dev logs don't mix with production logs

The mode is automatically detected based on the script location.

## Log File Format

- **Filename**: `termtools_YYYYMMDD.log`
- **Contents**: All output displayed in the GUI console (stdout and stderr)
- **Sessions**: Each run appends to the daily log file with a session header showing mode and working directory

## Log Rotation

Logs are organized by date. A new log file is created for each day. Consider manually archiving or deleting old logs periodically to manage disk space.

## What Gets Logged

- All print statements from TermTools operations
- Command outputs (git, python, etc.)
- Error messages and warnings
- Session timestamps (start and end)

## Notes

- ANSI color codes are stripped from log output
- Logs are written in real-time as operations execute
- Log files are properly closed when the application exits
