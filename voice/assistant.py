#!/usr/bin/env python3
"""
Voice assistant entry point for NovaForge.

Records short microphone clips, transcribes them via Ollama whisper,
routes the text through the active project chat driver, and optionally
speaks the response using a local TTS command (espeak by default).
"""
import argparse
import os
import platform
import select
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from core.project_manager import ProjectManager, ProjectError
from core.runtime.manager import ModelRuntimeManager, LLMRuntimeError
from core.model_manager import ModelManager, ModelManagerError


DEFAULT_SAMPLE_RATE = int(os.environ.get("VOICE_SAMPLE_RATE", "16000"))
DEFAULT_DURATION = float(os.environ.get("VOICE_RECORD_SECONDS", "8"))
DEFAULT_STT_MODEL = os.environ.get("VOICE_STT_MODEL", "whisper")
TTS_COMMAND = os.environ.get("VOICE_TTS_CMD")

VOICE_DEVICE_INDEX_RAW = os.environ.get("VOICE_DEVICE_INDEX")


def parse_device_spec(spec: str | None):
    if not spec:
        return None
    spec = spec.strip()
    if not spec:
        return None
    if spec.startswith("pulse:"):
        identifier = spec.split(":", 1)[1] or "default"
        return {"kind": "pulse", "id": identifier, "description": identifier}
    if spec.lower() == "default":
        return None
    try:
        idx = int(spec)
    except ValueError:
        return None
    return {"kind": "sounddevice", "id": idx, "name": f"Device {idx}"}


CURRENT_INPUT_DEVICE = parse_device_spec(VOICE_DEVICE_INDEX_RAW)

IS_WSL = (
    "WSL_DISTRO_NAME" in os.environ
    or "microsoft" in platform.release().lower()
    or Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists()
)


def info(msg: str):
    print(f"[Voice] {msg}")


def call_powershell(script: str) -> list[str]:
    if not IS_WSL or shutil.which("powershell.exe") is None:
        return []
    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                f"[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; {script}",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def get_windows_audio_inputs():
    """Get Windows audio recording devices from registry and device manager."""
    # Use a faster registry-based query
    script = r"""
$ErrorActionPreference = 'SilentlyContinue'

# Get active audio capture devices from registry
$capturePath = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Capture'
if (Test-Path $capturePath) {
    Get-ChildItem $capturePath | ForEach-Object {
        $propPath = Join-Path $_.PSPath 'Properties'
        if (Test-Path $propPath) {
            $name = (Get-ItemProperty $propPath).'{b3f8fa53-0004-438e-9003-51a46e139bfc},6'
            $state = (Get-ItemProperty $_.PSPath).DeviceState
            # DeviceState 1 = ACTIVE
            if ($name -and $state -eq 1) {
                $id = $_.PSChildName
                Write-Output "$id|$name"
            }
        }
    }
}
"""
    lines = call_powershell(script)
    devices = []
    seen_names = set()
    
    for line in lines:
        if "|" not in line:
            continue
        device_id, name = line.split("|", 1)
        # Avoid duplicates
        if name not in seen_names:
            seen_names.add(name)
            devices.append({"id": device_id, "name": name})
    
    return devices


def get_connected_bluetooth_devices():
    lines = call_powershell(
        r"$bts = Get-PnpDevice -Class 'Bluetooth' -PresentOnly | "
        r"Where-Object { $_.Status -eq 'OK' -and $_.FriendlyName }; "
        r"foreach ($bt in $bts) { '{0}|{1}' -f $bt.InstanceId, $bt.FriendlyName }"
    )
    devices = []
    for line in lines:
        if "|" not in line:
            devices.append({"id": line, "name": line})
            continue
        instance_id, name = line.split("|", 1)
        devices.append({"id": instance_id, "name": name})
    return devices


def set_windows_default_recording_device(device_name: str) -> bool:
    """Attempt to set the given device as Windows default recording device."""
    if not IS_WSL or shutil.which("powershell.exe") is None:
        return False
    
    # Escape quotes in device name
    escaped_name = device_name.replace('"', '`"').replace("'", "''")
    
    # Try using AudioDeviceCmdlets module first (if installed)
    script = f"""
$deviceName = '{escaped_name}'
try {{
    # Try AudioDeviceCmdlets module if available
    if (Get-Module -ListAvailable -Name AudioDeviceCmdlets) {{
        Import-Module AudioDeviceCmdlets -ErrorAction Stop
        $device = Get-AudioDevice -List | Where-Object {{$_.Name -like "*$deviceName*" -and $_.Type -eq "Recording"}} | Select-Object -First 1
        if ($device) {{
            Set-AudioDevice -ID $device.ID -ErrorAction Stop
            Write-Output "SUCCESS"
            exit 0
        }}
    }}
    
    # Fallback: Use Windows API via C# Add-Type
    $code = @"
using System;
using System.Runtime.InteropServices;

namespace AudioSwitch {{
    [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDeviceEnumerator {{
        int NotImpl1();
        int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppDevice);
        int GetDevice([MarshalAs(UnmanagedType.LPWStr)] string pwstrId, out IMMDevice ppDevice);
        int RegisterEndpointNotificationCallback(IntPtr pClient);
        int UnregisterEndpointNotificationCallback(IntPtr pClient);
    }}
    
    [Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDevice {{
        int Activate(ref Guid iid, int dwClsCtx, IntPtr pActivationParams, out IntPtr ppInterface);
        int OpenPropertyStore(int stgmAccess, out IntPtr ppProperties);
        int GetId([MarshalAs(UnmanagedType.LPWStr)] out string ppstrId);
        int GetState(out int pdwState);
    }}
    
    [Guid("F8679F50-850A-41CF-9C72-430F290290C8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IPolicyConfig {{
        int NotImpl1(); int NotImpl2(); int NotImpl3(); int NotImpl4();
        int NotImpl5(); int NotImpl6(); int NotImpl7(); int NotImpl8();
        int NotImpl9(); int NotImpl10();
        [PreserveSig] int SetDefaultEndpoint([MarshalAs(UnmanagedType.LPWStr)] string deviceId, uint role);
        int NotImpl11();
    }}
    
    public class AudioHelper {{
        public static int SetDefault(string deviceId) {{
            try {{
                var policyConfig = Activator.CreateInstance(Type.GetTypeFromCLSID(new Guid("870AF99C-171D-4F9E-AF0D-E63DF40C2BC9"))) as IPolicyConfig;
                return policyConfig.SetDefaultEndpoint(deviceId, 1); // 1 = eCommunications (recording)
            }} catch {{ return -1; }}
        }}
    }}
}}
"@
    
    Add-Type -TypeDefinition $code -ErrorAction Stop
    
    # Find the device ID by name
    Add-Type -AssemblyName System.Runtime.InteropServices
    $enumeratorGuid = [Guid]"A95664D2-9614-4F35-A746-DE8DB63617E6"
    $enumerator = [System.Activator]::CreateInstance([Type]::GetTypeFromCLSID([Guid]"BCDE0395-E52F-467C-8E3D-C4579291692E"))
    
    # Find device - this is simplified, may need registry query fallback
    $regPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices\\Audio\\Capture"
    $foundId = $null
    Get-ChildItem $regPath | ForEach-Object {{
        $props = Get-ItemProperty $_.PSPath
        $name = $props."(default)"
        if ($name -like "*$deviceName*") {{
            $foundId = $_.PSChildName
        }}
    }}
    
    if ($foundId) {{
        $result = [AudioSwitch.AudioHelper]::SetDefault($foundId)
        if ($result -eq 0) {{
            Write-Output "SUCCESS"
        }} else {{
            Write-Output "ERROR: SetDefault returned $result"
        }}
    }} else {{
        Write-Output "ERROR: Device not found in registry"
    }}
}} catch {{
    Write-Output "ERROR: $_"
}}
"""
    
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        output = result.stdout.strip()
        if "SUCCESS" in output:
            return True
        return False
    except Exception as exc:
        return False


def list_pulse_sources():
    if shutil.which("pactl") is None:
        return []
    default_source = None
    try:
        info_proc = subprocess.run(
            ["pactl", "info"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        for line in info_proc.stdout.splitlines():
            if line.startswith("Default Source:"):
                default_source = line.split(":", 1)[1].strip()
                break
    except (subprocess.TimeoutExpired, FileNotFoundError):
        default_source = None
    try:
        result = subprocess.run(
            ["pactl", "list", "sources"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    if result.returncode != 0:
        return []

    sources = []
    current = {}
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if line.startswith("Source #"):
            if current.get("name") and not current.get("name", "").endswith(".monitor"):
                sources.append(current)
            current = {"index": line.split("#", 1)[1].strip()}
            continue
        if line.startswith("Name:"):
            current["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("Description:"):
            current["description"] = line.split(":", 1)[1].strip()
    if current.get("name") and not current.get("name", "").endswith(".monitor"):
        sources.append(current)

    cleaned = []
    for src in sources:
        try:
            idx = int(src.get("index", 0))
        except ValueError:
            idx = None
        cleaned.append(
            {
                "name": src.get("name"),
                "description": src.get("description") or src.get("name"),
                "index": idx,
                "default": default_source is not None and src.get("name") == default_source,
            }
        )
    return [src for src in cleaned if src["name"]]


def list_input_devices():
    try:
        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
    except Exception as exc:
        info(f"Unable to enumerate audio devices: {exc}")
        devices = []
        hostapis = []

    default_input = None
    try:
        default_pair = sd.default.device
        if isinstance(default_pair, (list, tuple)) and default_pair:
            default_input = default_pair[0]
    except Exception:
        default_input = None

    capture_devices = []
    for idx, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) < 1:
            continue
        try:
            host_name = hostapis[dev["hostapi"]]["name"]
        except Exception:
            host_name = ""
        capture_devices.append(
            {
                "id": idx,
                "name": dev.get("name", f"Device {idx}"),
                "host": host_name,
                "default": default_input is not None and idx == default_input,
            }
        )
    bt_devices = get_connected_bluetooth_devices()
    windows_audio = get_windows_audio_inputs()
    pulse_sources = list_pulse_sources() if IS_WSL else []

    if not capture_devices and not pulse_sources:
        if bt_devices or windows_audio:
            info(
                "No ALSA/Pulse microphones detected inside WSL, but Windows reports connected audio devices. "
                "Ensure the WSL audio bridge is configured (see docs/WSL_AUDIO.md) so they appear as capture devices."
            )
        else:
            info("No microphones detected. Connect a microphone or review docs/WSL_AUDIO.md for setup tips.")
    elif pulse_sources and not capture_devices:
        info(
            "Detected PulseAudio sources from Windows/WSLg. Select one to capture audio even if ALSA devices are missing."
        )
    return capture_devices, bt_devices, windows_audio, pulse_sources


def describe_device(selection: dict | None) -> str:
    if selection is None:
        return "system default"
    kind = selection.get("kind")
    identifier = selection.get("id")
    if kind == "pulse":
        label = selection.get("description") or identifier
        return f"PulseAudio source '{label}'"
    if kind == "windows":
        label = selection.get("name") or identifier
        return f"Windows device '{label}'"
    if kind == "sounddevice":
        if "name" in selection:
            host = selection.get("host")
            label = selection.get("name")
            return f"{label}{f' via {host}' if host else ''}"
        try:
            dev = sd.query_devices(identifier)
            host_name = ""
            try:
                host_name = sd.query_hostapis()[dev["hostapi"]]["name"]
            except Exception:
                host_name = ""
            label = dev.get("name", f"Device {identifier}")
            return f"{label}{f' via {host_name}' if host_name else ''}"
        except Exception:
            return f"Device {identifier}"
    return "system default"


def prompt_for_input_device(current_selection: dict | None, force_selection: bool) -> dict | None:
    devices, bt_devices, windows_audio, pulse_sources = list_input_devices()

    linux_options: list[dict] = []
    for dev in devices:
        linux_options.append(
            {
                "kind": "sounddevice",
                "id": dev["id"],
                "name": dev["name"],
                "host": dev["host"],
                "default": dev["default"],
            }
        )
    for src in pulse_sources:
        linux_options.append(
            {
                "kind": "pulse",
                "id": src["name"],
                "description": src["description"],
                "default": src.get("default", False),
            }
        )
    windows_options = [{"kind": "windows", "id": win["id"], "name": win["name"]} for win in windows_audio]

    if not linux_options and not windows_options:
        if bt_devices:
            print("\nConnected Bluetooth devices (Windows):")
            for bt in bt_devices:
                print(f" - {bt['name']} [{bt['id']}]")
        info("⚠️ No microphones detected. Connect one or review docs/WSL_AUDIO.md for WSL instructions.")
        return None

    def is_current(selection: dict | None, option: dict) -> bool:
        return selection is not None and selection.get("kind") == option.get("kind") and selection.get("id") == option.get("id")

    def label_for(option: dict) -> str:
        if option["kind"] == "sounddevice":
            host_label = f"[{option.get('host', '')}]" if option.get("host") else ""
            return f"{option['name']} {host_label}".strip()
        if option["kind"] == "pulse":
            return f"{option['description']} (Pulse: {option['id']})"
        if option["kind"] == "windows":
            return f"{option['name']} (Windows host device)"
        return str(option.get("id"))

    option_map: dict[int, dict] = {}
    display_idx = 1
    if linux_options:
        print("\nAvailable microphones / audio sources:")
        for option in linux_options:
            option_map[display_idx] = option
            marker = "*" if is_current(current_selection, option) else " "
            default_marker = "(default)" if option.get("default") else ""
            print(f" {marker} {display_idx}. {label_for(option)} {default_marker}")
            display_idx += 1

    if windows_options:
        if not linux_options:
            info(
                "No Linux capture devices are exposed yet. Selecting a Windows device pins your preference so the WSL "
                "audio bridge can route it once configured."
            )
        print("\nWindows audio inputs (requires WSL audio bridge):")
        for option in windows_options:
            option_map[display_idx] = option
            marker = "*" if is_current(current_selection, option) else " "
            print(f" {marker} {display_idx}. {label_for(option)}")
            display_idx += 1

    while True:
        prompt = "Select microphone #"
        if current_selection is not None:
            prompt += f" (Enter to keep {describe_device(current_selection)})"
        prompt += ": "
        choice = input(prompt).strip()
        if not choice:
            if force_selection and current_selection is None:
                print("Microphone selection is required to continue.")
                continue
            return current_selection
        if choice.isdigit():
            idx = int(choice)
            if idx in option_map:
                return dict(option_map[idx])
        print("No microphone with that id. Try again.")


def ensure_microphone_selected(force_selection: bool = False) -> bool:
    global CURRENT_INPUT_DEVICE
    selection = prompt_for_input_device(CURRENT_INPUT_DEVICE, force_selection)
    if selection is not None:
        CURRENT_INPUT_DEVICE = selection
        
        # If user selected a Windows device, try to set it as default automatically
        if selection.get("kind") == "windows":
            device_name = selection.get("name", "")
            info(f"🔧 Setting '{device_name}' as Windows default recording device...")
            if set_windows_default_recording_device(device_name):
                info("✅ Successfully set as Windows default!")
            else:
                info("⚠️  Auto-config didn't work. Please set manually:")
                info(f"   Windows Settings → Sound → Input → Select '{device_name}'")

    if CURRENT_INPUT_DEVICE is None:
        info("🎧 Using system default microphone.")
    else:
        description = describe_device(CURRENT_INPUT_DEVICE)
        if CURRENT_INPUT_DEVICE.get("kind") == "windows":
            info(f"🎧 Selected Windows microphone: {description}")
        else:
            info(f"🎧 Using microphone: {description}")
    return selection is not None or CURRENT_INPUT_DEVICE is not None


def stdin_ready(stream) -> bool:
    try:
        readable, _, _ = select.select([stream], [], [], 0)
        return bool(readable)
    except (OSError, ValueError):
        return False


def diagnose_audio_failure(exc: Exception) -> str:
    lines = [f"Microphone capture failed: {exc}"]
    if IS_WSL:
        bridge = os.environ.get("NOVAFORGE_AUDIO_BRIDGE")
        pulse_sock = Path("/mnt/wslg/PulseServer")
        if bridge == "missing" or not pulse_sock.exists():
            lines.append(
                "WSL audio bridge not detected. Update WSLg or configure PulseAudio as described in docs/WSL_AUDIO.md."
            )
        else:
            lines.append(
                "WSL detected but no capture device was found. Ensure your Bluetooth mic is paired in Windows and"
                " that `arecord -l` inside WSL lists it."
            )
    lines.append("You can always type `/type` in voice mode until audio is available.")
    return "\n".join(lines)


def record_audio_via_sounddevice(duration: float, samplerate: int, device_index: int | None) -> Path:
    block_size = max(1024, int(samplerate * 0.25))
    stdin_stream = sys.stdin if sys.stdin.isatty() else None
    frames = []
    start_time = time.time()

    try:
        with sd.InputStream(
            samplerate=samplerate,
            channels=1,
            dtype=np.float32,
            device=device_index,
        ) as stream:
            while True:
                data, _ = stream.read(block_size)
                frames.append(np.copy(data))

                if stdin_stream and stdin_ready(stdin_stream):
                    stdin_stream.readline()
                    info("🎙️ Voice capture stopped.")
                    break

                if time.time() - start_time >= duration:
                    info("⏱️ Auto-stopped voice capture.")
                    break
    except sd.PortAudioError as exc:
        raise RuntimeError(diagnose_audio_failure(exc))

    if not frames:
        raise RuntimeError("No audio samples were captured. Check your microphone connection.")

    audio = np.concatenate(frames, axis=0)
    audio = np.squeeze(audio)
    temp_dir = Path(tempfile.mkdtemp(prefix="novaforge_voice_"))
    temp_path = temp_dir / "input.wav"
    int16_audio = np.int16(np.clip(audio, -1.0, 1.0) * 32767)
    wavfile.write(temp_path, samplerate, int16_audio)
    return temp_path


def record_audio_via_parec(duration: float, samplerate: int, source_name: str | None) -> Path:
    if shutil.which("parec") is None:
        raise RuntimeError("PulseAudio capture utility 'parec' not found. Install pulseaudio-utils to continue.")

    command = ["parec", "--format=s16le", f"--rate={samplerate}", "--channels=1"]
    if source_name and source_name != "default":
        command += ["--device", source_name]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise RuntimeError("PulseAudio capture utility 'parec' not found. Install pulseaudio-utils to continue.")

    chunk_size = max(4096, int(samplerate * 0.2) * 2)
    stdin_stream = sys.stdin if sys.stdin.isatty() else None
    frames = bytearray()
    start_time = time.time()
    stdout_stream = process.stdout

    try:
        while True:
            if stdout_stream:
                ready, _, _ = select.select([stdout_stream], [], [], 0.1)
                if stdout_stream in ready:
                    chunk = stdout_stream.read(chunk_size)
                    if chunk:
                        frames.extend(chunk)
                    elif process.poll() is not None:
                        break
            if stdin_stream and stdin_ready(stdin_stream):
                stdin_stream.readline()
                info("🎙️ Voice capture stopped.")
                break
            if time.time() - start_time >= duration:
                info("⏱️ Auto-stopped voice capture.")
                break
            if process.poll() is not None:
                break
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()

    if stdout_stream:
        try:
            remainder = stdout_stream.read()
            if remainder:
                frames.extend(remainder)
        except Exception:
            pass

    stderr_output = ""
    if process.stderr:
        stderr_output = process.stderr.read().strip()

    if not frames:
        message = "PulseAudio capture produced no audio."
        if stderr_output:
            message += f" Details: {stderr_output}"
        else:
            message += " Ensure your microphone is shared with WSLg and listed by 'pactl list sources'."
        raise RuntimeError(message)

    audio = np.frombuffer(bytes(frames), dtype=np.int16)
    if audio.size == 0:
        raise RuntimeError("PulseAudio capture yielded an empty buffer. Check your microphone connection.")

    temp_dir = Path(tempfile.mkdtemp(prefix="novaforge_voice_"))
    temp_path = temp_dir / "input.wav"
    wavfile.write(temp_path, samplerate, audio)
    return temp_path


def record_audio(duration: float, samplerate: int) -> Path:
    info(f"🎙️ Voice mode active. Press Enter again to stop (auto-stops in {duration:.1f}s).")
    selection = CURRENT_INPUT_DEVICE
    if selection:
        if selection.get("kind") == "pulse":
            return record_audio_via_parec(duration, samplerate, selection.get("id"))
        if selection.get("kind") == "windows":
            info(
                "Attempting to capture from the Windows default microphone via the WSL audio bridge. "
                "If recording fails, ensure `pactl list sources` works inside WSL."
            )
            return record_audio_via_parec(duration, samplerate, None)
    device_index = None
    if selection and selection.get("kind") == "sounddevice":
        device_index = selection.get("id")
    return record_audio_via_sounddevice(duration, samplerate, device_index)


def transcribe_audio(audio_path: Path, model_tag: str, ollama_cmd: str) -> str:
    if shutil.which(ollama_cmd) is None:
        raise RuntimeError(
            f"Ollama command '{ollama_cmd}' not found. Install Ollama or set OLLAMA_CMD."
        )

    info("Transcribing with Ollama...")
    result = subprocess.run(
        [ollama_cmd, "run", model_tag, f"file=@{audio_path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Ollama transcription failed: {result.stderr.strip() or result.stdout.strip()}"
        )

    lines = [line.strip("> ").strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("Received empty transcription from Ollama.")
    return lines[-1]


def speak_text(text: str):
    command = TTS_COMMAND.split() if TTS_COMMAND else None
    if not command and shutil.which("espeak"):
        command = ["espeak"]
    if not command:
        return

    try:
        subprocess.run(command + [text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def _ensure_active_model_config(pm: ProjectManager, project_root: str, config: dict) -> dict:
    """
    Makes sure the active project has an active model tag.
    If none is set, automatically assign the first available local model.
    """
    model_tag = config.get("active_model_tag")
    if model_tag:
        return config

    info("No active model configured; searching local manifest...")
    try:
        mm = ModelManager(project_root)
        available_models = mm.list_local_models()
    except ModelManagerError as exc:
        raise RuntimeError(f"Unable to inspect local models: {exc}")

    if not available_models:
        raise RuntimeError(
            "No active model is set and no local models were found. "
            "Download one via Manage Models before using the voice assistant."
        )

    selected_model = available_models[0]
    info(f"Automatically selecting '{selected_model}' for this project.")
    try:
        pm.set_active_model_for_project(selected_model)
    except ProjectError as exc:
        raise RuntimeError(f"Failed to set active model: {exc}")
    return pm.get_active_project_config()


def build_chat_driver(project_root: str):
    pm = ProjectManager(project_root)
    config = pm.get_active_project_config()
    config = _ensure_active_model_config(pm, project_root, config)

    mrm = ModelRuntimeManager(project_root)
    try:
        driver = mrm.get_driver(config)
    except LLMRuntimeError as exc:
        raise RuntimeError(str(exc))
    history = []
    system_prompt = config.get("system_prompt")
    if system_prompt:
        history.append({"role": "system", "content": system_prompt})

    return driver, history, config.get("project_name", "default")


def setup_wsl_audio_bridge():
    """Attempt to automatically configure WSL audio bridge."""
    if not IS_WSL:
        return True
    
    info("🔧 Checking WSL audio bridge configuration...")
    
    # Check if PulseAudio utils are installed
    if shutil.which("pactl") is None:
        info("📦 Installing pulseaudio-utils...")
        try:
            subprocess.run(
                ["sudo", "apt-get", "update", "-qq"],
                capture_output=True,
                timeout=30,
                check=False,
            )
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", "pulseaudio-utils"],
                capture_output=True,
                timeout=60,
                check=False,
            )
            info("✅ Installed pulseaudio-utils")
        except Exception as exc:
            info(f"⚠️  Could not install pulseaudio-utils: {exc}")
    
    # Test if PulseAudio is accessible
    pulse_server = os.environ.get("PULSE_SERVER", "unix:/mnt/wslg/PulseServer")
    test_env = os.environ.copy()
    test_env["PULSE_SERVER"] = pulse_server
    
    try:
        result = subprocess.run(
            ["pactl", "info"],
            env=test_env,
            capture_output=True,
            timeout=3,
            check=False,
        )
        if result.returncode == 0:
            info("✅ WSL audio bridge is working!")
            return True
    except Exception:
        pass
    
    # If bridge is broken, try to fix common issues
    info("⚠️  WSL audio bridge not responding. Attempting fixes...")
    
    # Fix 1: Check runtime directory permissions
    runtime_dir = Path("/mnt/wslg/runtime-dir")
    if runtime_dir.exists():
        try:
            # Ensure proper permissions
            subprocess.run(["chmod", "700", str(runtime_dir)], check=False, capture_output=True)
            info("   Fixed runtime directory permissions")
        except Exception:
            pass
    
    # Fix 2: Try alternative pulse socket
    alt_socket = "/mnt/wslg/runtime-dir/pulse/native"
    if Path(alt_socket).exists():
        info(f"   Trying alternative socket: {alt_socket}")
        os.environ["PULSE_SERVER"] = f"unix:{alt_socket}"
        try:
            result = subprocess.run(
                ["pactl", "info"],
                env=os.environ.copy(),
                capture_output=True,
                timeout=3,
                check=False,
            )
            if result.returncode == 0:
                info("✅ Connected using alternative socket!")
                return True
        except Exception:
            pass
    
    # Bridge is broken - offer automatic fix
    info("❌ WSL audio bridge is not accessible.")
    info("")
    info("💡 This can be fixed automatically by restarting WSL.")
    info("")
    
    # Check if user wants auto-fix
    try:
        response = input("🔧 Restart WSL now to fix audio? (y/n): ").strip().lower()
        if response == 'y':
            fix_script = Path(__file__).parent.parent / "scripts" / "fix_wsl_audio.sh"
            if fix_script.exists():
                info("🔄 Restarting WSL...")
                subprocess.run([str(fix_script)], check=False)
                # If we're still here, user cancelled
                return False
            else:
                info("⚠️  Fix script not found. Manual restart needed:")
                info("   Run from Windows PowerShell: wsl --shutdown")
    except (KeyboardInterrupt, EOFError):
        print()
    
    info("")
    info("💡 Until fixed, use /type to interact without voice recording.")
    info("   See docs/WSL_AUDIO.md for detailed troubleshooting.")
    info("")
    
    return False


def voice_loop(project_root: str, ollama_cmd: str):
    driver, history, project_name = build_chat_driver(project_root)

    # Auto-setup WSL audio if needed
    audio_working = True
    if IS_WSL:
        audio_working = setup_wsl_audio_bridge()
    
    # Select microphone
    mic_ready = ensure_microphone_selected(force_selection=True)
    if not mic_ready:
        info("Voice capture may fail until a microphone is available.")
    
    # Set initial mode based on audio availability
    if not audio_working:
        info("🔤 Starting in TEXT MODE - type your messages instead of speaking.")
        info(f"Voice assistant ready for project '{project_name}'. Commands: /type, /mic, /exit")
        # Auto-enter /type mode
        while True:
            user_input = input("\n💬 Type your message (or /mic to retry voice, /exit to quit): ").strip()
            lowered = user_input.lower()
            
            if lowered == "/exit":
                info("Ending voice session.")
                break
            
            if lowered == "/mic":
                info("🎙️ Attempting to switch to voice mode...")
                if setup_wsl_audio_bridge():
                    audio_working = True
                    info("✅ Switched to VOICE MODE")
                    break
                else:
                    continue
            
            if not user_input:
                info("⚠️  Please type a message or use /exit to quit.")
                continue
            
            # Process typed input
            history.append({"role": "user", "content": user_input})
            try:
                print("🤖 Assistant: ", end="", flush=True)
                response = ""
                for token in driver.generate(history, stream=True):
                    response += token
                    print(token, end="", flush=True)
                print("\n")
                history.append({"role": "assistant", "content": response})
            except Exception as exc:
                info(f"❌ Chat failed: {exc}")
                history.pop()
    
    if not audio_working:
        return
    
    info(
        f"Voice assistant ready for project '{project_name}'. Commands: "
        "press Enter for voice, /type to type, /mic to change microphone, /exit to quit."
    )

    while True:
        user_input = input("\nPress Enter to capture voice, or command [/type, /mic, /exit]: ").strip()
        lowered = user_input.lower()

        if lowered == "/exit":
            info("Ending voice session.")
            break

        if lowered == "/mic":
            ensure_microphone_selected(force_selection=True)
            continue

        transcript = ""
        source_label = "transcribed"

        if lowered.startswith("/type"):
            manual_input = user_input[5:].strip()
            if not manual_input:
                manual_input = input("Type your message: ").strip()
            transcript = manual_input
            source_label = "typed"
            if not transcript:
                continue
        elif user_input:
            info("Unknown command. Use /type, /mic, or /exit.")
            continue
        else:
            try:
                audio_path = record_audio(DEFAULT_DURATION, DEFAULT_SAMPLE_RATE)
            except KeyboardInterrupt:
                print()
                info("Recording cancelled.")
                continue
            except Exception as exc:
                info(f"❌ Recording failed: {exc}")
                continue

            try:
                transcript = transcribe_audio(audio_path, DEFAULT_STT_MODEL, ollama_cmd)
            except Exception as exc:
                info(f"❌ Transcription failed: {exc}")
                continue
            finally:
                try:
                    audio_path.unlink(missing_ok=True)
                    audio_path.parent.rmdir()
                except Exception:
                    pass

        if not transcript:
            continue

        info(f"YOU ({source_label}): {transcript}")
        history.append({"role": "user", "content": transcript})

        print("AI> ", end="", flush=True)
        response = ""
        try:
            for token in driver.generate(history, stream=True):
                response += token
                print(token, end="", flush=True)
            print()
        except (LLMRuntimeError, Exception) as exc:
            print(f"\n❌ LLM Error: {exc}")
            continue

        if response.strip():
            speak_text(response)
            history.append({"role": "assistant", "content": response})


def parse_args():
    parser = argparse.ArgumentParser(description="NovaForge Voice Assistant")
    parser.add_argument("project_root", help="Absolute path to the NovaForge project root.")
    return parser.parse_args()


def main():
    args = parse_args()
    project_root = args.project_root

    if not Path(project_root).is_dir():
        print("Invalid project root. Exiting.")
        sys.exit(1)

    try:
        voice_loop(project_root, os.environ.get("OLLAMA_CMD", "ollama"))
    except (ProjectError, RuntimeError) as exc:
        print(f"Voice assistant error: {exc}")
    except KeyboardInterrupt:
        print("\nVoice session interrupted.")


if __name__ == "__main__":
    main()
