local wezterm = require("wezterm")

return {
  font = wezterm.font_with_fallback({
    "JetBrainsMono Nerd Font",
    "FiraCode Nerd Font",
    "Hack Nerd Font",
  }),
  font_size = 13.5,

  enable_wayland = true,
  hide_tab_bar_if_only_one_tab = true,
  use_fancy_tab_bar = false,

  color_scheme = "Catppuccin Mocha",
  window_background_opacity = 0.95,
  text_background_opacity = 1.0,
  window_decorations = "RESIZE",
  adjust_window_size_when_changing_font_size = false,

  window_padding = {
    left = 8,
    right = 8,
    top = 4,
    bottom = 4,
  },

  default_prog = { "/usr/bin/zsh", "-l" },
  enable_scroll_bar = false,

  -- Clean title
  set_environment_variables = {
    TERM = "wezterm",
  },
}

