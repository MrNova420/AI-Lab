# Windows Commander Agent - PowerShell Script
# Called from WSL to control Windows system

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [string]$Args
)

# Load Windows Forms for mouse/keyboard control
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Execute-Command {
    param($cmd, $arguments)
    
    $result = @{
        success = $false
        action = $cmd
        message = ""
    }
    
    try {
        switch ($cmd) {
            "mouse_move" {
                $coords = $arguments | ConvertFrom-Json
                [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($coords.x, $coords.y)
                $result.success = $true
                $result.message = "Moved mouse to ($($coords.x), $($coords.y))"
            }
            
            "mouse_click" {
                $params = $arguments | ConvertFrom-Json
                Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class Mouse {
                    [DllImport("user32.dll")]
                    public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
                    public const int MOUSEEVENTF_LEFTDOWN = 0x02;
                    public const int MOUSEEVENTF_LEFTUP = 0x04;
                    public const int MOUSEEVENTF_RIGHTDOWN = 0x08;
                    public const int MOUSEEVENTF_RIGHTUP = 0x10;
                }
"@
                if ($params.button -eq "left") {
                    [Mouse]::mouse_event(0x02, 0, 0, 0, 0)  # Left down
                    Start-Sleep -Milliseconds 50
                    [Mouse]::mouse_event(0x04, 0, 0, 0, 0)  # Left up
                }
                $result.success = $true
                $result.message = "Clicked $($params.button) mouse button"
            }
            
            "keyboard_type" {
                $params = $arguments | ConvertFrom-Json
                [System.Windows.Forms.SendKeys]::SendWait($params.text)
                $result.success = $true
                $result.message = "Typed text"
            }
            
            "keyboard_press" {
                $params = $arguments | ConvertFrom-Json
                [System.Windows.Forms.SendKeys]::SendWait("{$($params.key)}")
                $result.success = $true
                $result.message = "Pressed $($params.key)"
            }
            
            "check_app" {
                $params = $arguments | ConvertFrom-Json
                $app = $params.app
                
                # App name mapping
                $appMap = @{
                    "steam" = "steam.exe"
                    "discord" = "Discord.exe"
                    "chrome" = "chrome.exe"
                    "code" = "Code.exe"
                    "vscode" = "Code.exe"
                    "notepad" = "notepad.exe"
                    "calculator" = "calc.exe"
                    "calc" = "calc.exe"
                    "spotify" = "Spotify.exe"
                    "obs" = "obs64.exe"
                    "obs64" = "obs64.exe"
                    "vlc" = "vlc.exe"
                }
                
                $exeName = if ($appMap.ContainsKey($app.ToLower())) { $appMap[$app.ToLower()] } else { "$app.exe" }
                $processName = $exeName.Replace('.exe', '')
                
                # Check if running
                $running = Get-Process -Name $processName -ErrorAction SilentlyContinue
                if ($running) {
                    $result.success = $true
                    $result.message = "FOUND_RUNNING"
                    return $result | ConvertTo-Json
                }
                
                # Check common install paths
                $paths = @(
                    "C:\Program Files\$app",
                    "C:\Program Files (x86)\$app",
                    "$env:LOCALAPPDATA\$app",
                    "$env:APPDATA\$app"
                )
                
                foreach ($path in $paths) {
                    if (Test-Path $path) {
                        $result.success = $true
                        $result.message = "FOUND_INSTALLED"
                        return $result | ConvertTo-Json
                    }
                }
                
                # Check via Get-Command
                $cmd = Get-Command $exeName -ErrorAction SilentlyContinue
                if ($cmd) {
                    $result.success = $true
                    $result.message = "FOUND_INSTALLED"
                    return $result | ConvertTo-Json
                }
                
                $result.success = $false
                $result.message = "NOT_FOUND"
            }
            
            "open_app" {
                $params = $arguments | ConvertFrom-Json
                Start-Process $params.app
                $result.success = $true
                $result.message = "Opened $($params.app)"
            }
            
            "open_url" {
                $params = $arguments | ConvertFrom-Json
                Start-Process $params.url
                $result.success = $true
                $result.message = "Opened $($params.url)"
            }
            
            "screenshot" {
                Add-Type -AssemblyName System.Drawing
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
                
                $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
                $filename = "screenshot_$timestamp.png"
                $path = "$env:USERPROFILE\Downloads\$filename"
                $bitmap.Save($path)
                
                $result.success = $true
                $result.message = "Screenshot saved to $path"
            }
            
            "clipboard_copy" {
                $params = $arguments | ConvertFrom-Json
                Set-Clipboard -Value $params.text
                $result.success = $true
                $result.message = "Copied to clipboard"
            }
            
            "list_windows" {
                Add-Type @"
                using System;
                using System.Runtime.InteropServices;
                using System.Text;
                public class WindowHelper {
                    [DllImport("user32.dll")]
                    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
                    [DllImport("user32.dll")]
                    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
                    [DllImport("user32.dll")]
                    public static extern bool IsWindowVisible(IntPtr hWnd);
                    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
                }
"@
                $windows = @()
                [WindowHelper]::EnumWindows({
                    param($hwnd, $lparam)
                    if ([WindowHelper]::IsWindowVisible($hwnd)) {
                        $sb = New-Object System.Text.StringBuilder 256
                        [WindowHelper]::GetWindowText($hwnd, $sb, 256)
                        if ($sb.Length -gt 0) {
                            $windows += $sb.ToString()
                        }
                    }
                    return $true
                }, [IntPtr]::Zero)
                
                $result.success = $true
                $result.message = "Found $($windows.Count) windows"
                $result.data = $windows
            }
            
            default {
                $result.message = "Unknown command: $cmd"
            }
        }
    }
    catch {
        $result.success = $false
        $result.message = "Error: $($_.Exception.Message)"
    }
    
    return $result
}

# Execute command and return JSON
$result = Execute-Command -cmd $Command -arguments $Args
$result | ConvertTo-Json -Compress
