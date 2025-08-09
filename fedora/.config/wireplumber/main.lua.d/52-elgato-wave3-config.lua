-- Configure Elgato Wave 3
rule = {
  matches = {
    {
      { "node.name", "matches", "alsa_*.usb-Elgato_Systems_Elgato_Wave_3*" },
    },
  },
  apply_properties = {
    ["audio.rate"] = 48000,
    ["audio.channels"] = 1,
    ["priority.session"] = 2000,
    ["priority.driver"] = 2000,
  },
}

table.insert(alsa_monitor.rules,rule)