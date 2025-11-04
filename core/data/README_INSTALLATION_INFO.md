# Installation Info Configuration

## installation_info.json

This file contains metadata about the TermTools installation and configuration.

### Fields:

- **installation_timestamp**: When TermTools was installed
- **repository**: GitHub repository path
- **remote_commit_hash**: Git commit hash of the installed version
- **installer_version**: Version of the installer used
- **installation_path**: Where TermTools is installed
- **dev_mode**: Controls logging behavior (see below)

### Dev Mode Flag

The `dev_mode` flag controls where log files are created:

#### `"dev_mode": true` (Development Mode)
- Log files are created at: `<current_directory>/core/data/logs/`
- Where `<current_directory>` is the directory where you right-clicked to launch TermTools
- Useful for testing and development

#### `"dev_mode": false` (Production Mode)
- Log files are created at: `C:\Program Files\BasusTools\TermTools\core\data\logs\`
- Standard production behavior
- Logs are centralized regardless of where TermTools is launched from

### Manual Configuration

You can manually toggle between dev and production mode by editing `installation_info.json`:

```json
{
  "dev_mode": true   // Set to false for production mode
}
```

**Note**: Changes take effect the next time TermTools is launched.
