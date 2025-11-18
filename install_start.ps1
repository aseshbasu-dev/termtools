# ===============================
# PowerShell Script: install_python.ps1
# Auto-elevates if needed, installs system-wide or user-only safely

# main installer
# Bootstrap and run the this file(with "Run as Admininistrator" selected) as:
# $u='https://raw.githubusercontent.com/aseshbasu-dev/termtools/refs/heads/main/install_start.ps1'; $f=Join-Path $env:TEMP 'bootstrap_and_run.ps1'; Invoke-WebRequest -Uri $u -OutFile $f -UseBasicParsing; Start-Process -FilePath 'powershell' -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$f`""
# 
# downloads python if not exists, installs it system-wide if run as admin, else per-user
# starts the installation silently, adds to PATH
# starts the install_python.ps1 script to continue installation - create fodler in Program files, create .vevnv, install requirements.txt packages, add to context menu, etc.
# 


# ===============================

function Write-Info($msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Cyan
}

function Is-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# --- 0. Self-elevate if not admin ---
if (-not (Is-Admin)) {
    Write-Info "Current session is not elevated. Requesting admin rights..."
    Write-Info "A UAC prompt will appear - please click 'Yes' to continue."
    
    $scriptPath = $PSCommandPath
    $arguments = "-ExecutionPolicy Bypass -Command `"& '$scriptPath'; Read-Host 'Press Enter to exit'`""
    
    try {
        Start-Process -FilePath "powershell" -ArgumentList $arguments -Verb RunAs -Wait
        Write-Info "Elevated script completed. Check the elevated window for results."
        exit
    }
    catch {
        Write-Info "User denied elevation or elevation failed. Installing for current user only."
        $NoAdmin = $true
    }
}
else {
    Write-Info "Already running as Administrator."
    $NoAdmin = $false
}

# --- 1. Define variables ---
$pythonVersion = "3.12.7"
$installerUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerPath = "$env:TEMP\python_installer.exe"

# --- 2. Check if Python already installed ---
Write-Info "Checking if Python is already installed..."
$pythonExists = Get-Command python -ErrorAction SilentlyContinue
if ($pythonExists) {
    $version = python --version 2>&1
    Write-Info "Python already installed: $version"
    Write-Host "`n[OK] Python is available: $version" -ForegroundColor Green
}
else {
    Write-Info "Python not found. Starting installation..."
    
    # --- 3. Download installer ---
    Write-Info "Downloading Python $pythonVersion..."
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing

    # --- 4. Choose install mode ---
    if (-not $NoAdmin) {
        Write-Info "Installing system-wide..."
        $args = "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
    }
    else {
        Write-Info "Installing for current user..."
        $args = "/quiet PrependPath=1 Include_test=0"
    }

    # --- 5. Install silently ---
    Start-Process -FilePath $installerPath -ArgumentList $args -Wait

    # --- 6. Cleanup ---
    Remove-Item $installerPath -Force

    # --- 7. Verify installation ---
    Write-Info "Verifying installation..."
    $pythonExists = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonExists) {
        $version = python --version 2>&1
        Write-Host "`n[OK] Python successfully installed: $version" -ForegroundColor Green
    }
    else {
        Write-Host "`n[ERROR] Python installation failed. Cannot proceed with TermTools installation." -ForegroundColor Red
        Write-Host "`n=== Installation Failed ===" -ForegroundColor Red
        Write-Host "Press any key to exit..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}

# --- 8. At this point, Python is confirmed available (either was already there or just installed) ---
Write-Info "Python is confirmed available. Proceeding with TermTools installation..."
$termtoolsInstaller = "https://raw.githubusercontent.com/aseshbasu-dev/termtools/refs/heads/main/install_termtools.py"

$installSuccess = $false

if (-not (Is-Admin)) {
    Write-Info "TermTools installation requires admin rights. Elevating..."
    Write-Info "A UAC prompt will appear for TermTools installation - please click 'Yes'."
    
    $installCommand = "try { `$content = Invoke-WebRequest -Uri '$termtoolsInstaller' -UseBasicParsing | Select-Object -ExpandProperty Content; `$content | python -; Write-Host '`n[SUCCESS] TermTools installation complete!' -ForegroundColor Green; exit 0 } catch { Write-Host '`n[ERROR] TermTools installation failed: `$(`$_.Exception.Message)' -ForegroundColor Red; Read-Host 'Press Enter to exit'; exit 1 }"
    
    try {
        $process = Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy Bypass -Command `"$installCommand`"" -Verb RunAs -Wait -PassThru
        if ($process.ExitCode -eq 0) {
            Write-Host "`n[SUCCESS] TermTools installation completed successfully!" -ForegroundColor Green
            $installSuccess = $true
        }
        else {
            Write-Host "`n[ERROR] TermTools installation failed (exit code: $($process.ExitCode))" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "`n[ERROR] Failed to elevate for TermTools installation: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "You can manually run as admin: (Invoke-WebRequest -UseBasicParsing '$termtoolsInstaller').Content | python -" -ForegroundColor Yellow
    }
}
else {
    Write-Info "Already elevated. Installing TermTools directly..."
    try {
        $content = Invoke-WebRequest -Uri $termtoolsInstaller -UseBasicParsing | Select-Object -ExpandProperty Content
        $content | python -
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n[SUCCESS] TermTools installation complete! TermTools is now available in your right-click context menu." -ForegroundColor Green
            $installSuccess = $true
        }
        else {
            Write-Host "`n[ERROR] TermTools installation failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "`n[ERROR] Failed to install TermTools: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "You can manually run: (Invoke-WebRequest -UseBasicParsing '$termtoolsInstaller').Content | python -" -ForegroundColor Yellow
    }
}

if ($installSuccess) {
    Write-Host "`n=== Installation Complete ===" -ForegroundColor Green
}
else {
    Write-Host "`n=== Installation Failed ===" -ForegroundColor Red
}
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
