# WSL Audio & Microphone Guide

NovaForge’s voice mode depends on PulseAudio/ALSA input devices. On native Linux they exist automatically, but WSL needs a bridge to Windows audio. Follow these steps to expose your laptop or Bluetooth microphone to WSL:

1. **Update WSL / enable WSLg (Windows 11)**  
   ```powershell
   wsl --update
   wsl --shutdown
   ```  
   Re-launch Ubuntu from the Start menu. WSLg ships a PulseAudio server inside `\\wslg`.

2. **Pair and allow the microphone in Windows**  
   - Pair the Bluetooth headset in *Windows Settings → Bluetooth & devices*.  
   - In *Privacy & security → Microphone*, ensure “Let desktop apps access your microphone” is ON.

3. **Bridge PulseAudio into WSL**  
   Inside WSL the `forge.sh` launcher attempts to export `PULSE_SERVER=unix:/mnt/wslg/PulseServer` and `ALSA_CONFIG_PATH=/mnt/wslg/alsa-conf/alsa.conf`. If you disabled WSLg or are on Windows 10, install a PulseAudio server manually (e.g. [VcXsrv + PulseAudio](https://github.com/microsoft/WSL/issues/7763#issuecomment-1341324196)) and set:
   ```bash
   echo 'export PULSE_SERVER=tcp:127.0.0.1' >> ~/.bashrc
   echo 'export ALSA_CONFIG_PATH=/etc/alsa/wsl.conf' >> ~/.bashrc
   ```

4. **Validate the bridge**  
   In WSL run:
   ```bash
   sudo apt install -y pulseaudio-utils
    pactl info | grep 'Server String'
    pactl list short sources
    arecord -l
   ```
   You should see at least one capture device or PulseAudio source. If you still see “no soundcards found”, the Windows audio server is not reachable.

5. **Select devices (optional)**  
   - Set `VOICE_DEVICE_INDEX=<number>` to pin an ALSA/PortAudio device id.  
   - Set `VOICE_DEVICE_INDEX=pulse:<source_name>` to pin a PulseAudio/WSLg source (copy the name from `pactl list sources`).  
   - The in-app `/mic` picker now lists both kinds automatically—pick a PulseAudio source when no ALSA devices appear.  
   - If only Windows host devices show up, select one and the system will automatically attempt to set it as the Windows default recording device so the WSL audio bridge can capture from it.

Once `arecord -l` or `pactl list sources` shows your Bluetooth headset, `voice/assistant.py` can record normally. Until then, use `/type` inside voice mode for manual input.
