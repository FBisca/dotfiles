-- Disable unused audio devices
rule = {
  matches = {
    {
      -- Disable WD15 Dock audio
      { "node.name", "matches", "alsa_*.usb-Generic_USB_Audio*" },
    },
    {
      -- Disable HDMI audio from Intel
      { "node.name", "matches", "alsa_*.pci-0000_00_1f.3.*hdmi*" },
    },
    {
      -- Disable HDMI audio from NVidia
      { "node.name", "matches", "alsa_*.pci-0000_01_00.1.*" },
    },
  },
  apply_properties = {
    ["node.disabled"] = true,
  },
}

table.insert(alsa_monitor.rules,rule)