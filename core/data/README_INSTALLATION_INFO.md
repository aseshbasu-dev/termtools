# Installation Info Configuration

## installation_info.json

This file contains metadata about the TermTools installation and configuration.

**Location**: `C:\Users\<username>\AppData\Local\BasusTools\TermTools\installation_info.json`

### Fields:

- **installation_timestamp**: When TermTools was installed
- **repository**: GitHub repository path
- **remote_commit_hash**: Git commit hash of the installed version
- **installer_version**: Version of the installer used
- **installation_path**: Where TermTools program files are installed (Program Files)
- **data_directory**: Where writable data files are stored (AppData\Local)

## Data File Locations

All writable data files (logs, stats, state files) are stored in the user's AppData directory to avoid permission issues:

**Windows**: `C:\Users\<username>\AppData\Local\BasusTools\TermTools\`
**Unix/Linux/Mac**: `~/.local/share/BasusTools/TermTools/`

### Files stored in data directory:
- **logs/**: Daily log files (`termtools_YYYYMMDD.log`)
- **installation_info.json**: Installation metadata
- **pomodoro_stats.json**: Pomodoro timer statistics
- **shutdown_state.json**: Power manager state

### Why AppData?

Program Files requires administrator permissions for write operations. By storing writable data in AppData\Local, TermTools can:
- Write logs and save state without admin rights
- Work correctly in multi-user environments
- Follow Windows best practices for application data storage

**Note**: The TermTools application itself remains in `C:\Program Files\BasusTools\TermTools\` (read-only), while all user data is in AppData (writable).
