#!/bin/bash
# Script to fix Discord and Google Meet audio issues

echo "Setting up audio for Discord and Google Meet..."

# Ensure Elgato Wave 3 is set as default input
pactl set-default-source alsa_input.usb-Elgato_Systems_Elgato_Wave_3_A011A451118R4C-00.mono-fallback

# Ensure QCY H3 Pro is set as default output (if connected)
if pactl list sinks short | grep -q "bluez_output.84_AC_60_72_32_93"; then
    pactl set-default-sink bluez_output.84_AC_60_72_32_93.1
    echo "✓ QCY H3 Pro set as default output"
else
    # Fallback to built-in audio if Bluetooth not connected
    pactl set-default-sink alsa_output.pci-0000_00_1f.3.analog-stereo
    echo "⚠ QCY H3 Pro not connected, using built-in audio"
fi

# Set proper volumes
pactl set-source-volume @DEFAULT_SOURCE@ 100%
pactl set-sink-volume @DEFAULT_SINK@ 80%

# Kill and restart Discord if running (to pick up new audio settings)
if pgrep -x "Discord" > /dev/null; then
    echo "Restarting Discord to apply audio settings..."
    pkill -x Discord
    sleep 2
    discord &>/dev/null &
    disown
fi

echo "✓ Audio setup complete!"
echo ""
echo "Current settings:"
echo "  Input:  $(pactl get-default-source)"
echo "  Output: $(pactl get-default-sink)"