# TermTools Logs

This directory contains log files for TermTools sessions.

## Log File Format

- **Filename**: `termtools_YYYYMMDD.log`
- **Contents**: All output displayed in the GUI console (stdout and stderr)
- **Sessions**: Each run appends to the daily log file with a session header

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
