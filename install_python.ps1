# ===============================
# PowerShell Script: install_python.ps1
# Auto-elevates if needed, installs system-wide or user-only safely

# main installer
# Bootstrap and run the this file(with "Run as Admininistrator" selected) as:
# $u='https://raw.githubusercontent.com/aseshbasu-dev/termtools/main/bootstrap_and_run.ps1'; $f=Join-Path $env:TEMP 'bootstrap_and_run.ps1'; Invoke-WebRequest -Uri $u -OutFile $f -UseBasicParsing; Start-Process -FilePath 'powershell' -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$f`""
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
    Write-Info "Requesting admin rights..."
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell"
    $psi.Arguments = "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    $psi.Verb = "runas"
    try {
        [System.Diagnostics.Process]::Start($psi) | Out-Null
        exit
    } catch {
        Write-Info "User denied elevation. Installing for current user only."
        $NoAdmin = $true
    }
} else {
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
    Write-Info "Script finished — safe to rerun anytime."
    exit 0
}

# --- 3. Download installer ---
Write-Info "Downloading Python $pythonVersion..."
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing

# --- 4. Choose install mode ---
if (-not $NoAdmin) {
    Write-Info "Installing system-wide..."
    $args = "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
} else {
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
    Write-Host "`n✅ Python successfully installed: $version" -ForegroundColor Green
    
    # --- 8. Continue with TermTools installation ---
    Write-Info "Now installing TermTools..."
    $termtoolsInstaller = "https://raw.githubusercontent.com/aseshbasu-dev/termtools/main/install_termtools.py"
    try {
        $content = Invoke-WebRequest -Uri $termtoolsInstaller -UseBasicParsing | Select-Object -ExpandProperty Content
        $content | python -
        Write-Host "`n🎉 Installation complete! TermTools is now available in your right-click context menu." -ForegroundColor Green
    } catch {
        Write-Host "`n❌ Failed to install TermTools: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "You can manually run: (Invoke-WebRequest -UseBasicParsing '$termtoolsInstaller').Content | python -" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n❌ Python installation failed. Try running PowerShell as Administrator." -ForegroundColor Red
}

Start-Sleep -Seconds 3
