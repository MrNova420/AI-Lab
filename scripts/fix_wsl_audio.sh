#!/bin/bash
# Fix WSL audio bridge by restarting WSL from Windows

echo "🔧 Fixing WSL audio bridge..."
echo ""
echo "This will:"
echo "  1. Create a temporary PowerShell script"
echo "  2. Restart WSL to fix PulseAudio"
echo "  3. Automatically restart this session"
echo ""

# Create temp PowerShell script
TEMP_PS1="/mnt/c/Temp/wsl_audio_fix_$$.ps1"
cat > "$TEMP_PS1" << 'PSEOF'
Write-Host "Shutting down WSL to reset audio bridge..." -ForegroundColor Yellow
wsl --shutdown
Start-Sleep -Seconds 3
Write-Host "Restarting WSL..." -ForegroundColor Green
wsl -d Ubuntu bash -c "cd ~/ai-forge && ./forge.sh"
PSEOF

echo "⚠️  This will close your current WSL session and restart it."
read -p "Continue? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Restarting WSL..."
    # Execute the PowerShell script from Windows
    powershell.exe -ExecutionPolicy Bypass -File "$TEMP_PS1"
    exit 0
else
    echo "Cancelled."
    rm -f "$TEMP_PS1"
    exit 1
fi
