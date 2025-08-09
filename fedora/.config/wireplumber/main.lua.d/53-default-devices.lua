-- Set default audio devices
rule = {
  matches = {
    {
      -- QCY H3 Pro as default output when connected
      { "node.name", "matches", "bluez_output.84_AC_60_72_32_93*" },
    },
  },
  apply_properties = {
    ["priority.session"] = 3000,
    ["priority.driver"] = 3000,
  },
}

table.insert(bluez_monitor.rules,rule)

-- Elgato Wave 3 as default input
rule2 = {
  matches = {
    {
      { "node.name", "matches", "alsa_input.usb-Elgato_Systems_Elgato_Wave_3*" },
    },
  },
  apply_properties = {
    ["priority.session"] = 3000,
    ["priority.driver"] = 3000,
  },
}

table.insert(alsa_monitor.rules,rule2)