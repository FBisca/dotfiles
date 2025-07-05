vim.g.mapleader = " "

vim.opt.rtp:prepend(vim.fn.stdpath("config") .. "/lazy/lazy.nvim")
require("lazy").setup({ import = "plugins" })

require("plugins.nvimtree")

require("keymaps.telescope")
require("keymaps.nvimtree")

