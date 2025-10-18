# 🧩 Neovim Configuration

A modern, fast Neovim setup written in Lua with essential plugins for development.

## 🧠 What This Is

✅ **Fast**: Written in Lua, significantly faster than Vimscript  
🧠 **Modern**: Uses lazy.nvim for plugin management and modern Lua APIs  
🧩 **Modular**: Clean separation of plugins, keymaps, and configuration  
🔧 **Developer-focused**: Optimized for TypeScript/JavaScript development  

## ✨ Features

### **Plugin Management**
- **Lazy.nvim** - Fast, modern plugin manager
- **Automatic installation** - Plugins install automatically on first run
- **Lazy loading** - Plugins load only when needed for better performance

### **File Management**
- **Nvim-tree** - File explorer with tree view
- **Telescope** - Fuzzy finder for files, buffers, and more
- **Devicons** - File type icons in the file tree

### **Code Intelligence**
- **LSP** - Language Server Protocol support
- **Treesitter** - Syntax highlighting and parsing
- **Auto-completion** - Smart code completion with nvim-cmp
- **Formatting** - Prettier and ESLint integration

### **Language Support**
- TypeScript/TSX
- JavaScript
- JSON
- Lua
- And more via Treesitter

## 🚀 Key Bindings

### **File Management**
| Key | Action | Description |
|-----|--------|-------------|
| `<leader>e` | Toggle file tree | Open/close NvimTree |
| `<leader>ff` | Find files | Telescope file finder |
| `<leader>fg` | Live grep | Search in files |
| `<leader>fb` | Find buffers | Switch between open files |
| `<leader>fh` | Help tags | Search help documentation |

### **Leader Key**
- **Leader**: `<Space>` (spacebar)

## 📁 Structure

```
nvim/
├── .config/nvim/
│   ├── init.lua              # Main configuration
│   └── lua/
│       ├── plugins/          # Plugin configurations
│       │   ├── nvimtree.lua  # File tree setup
│       │   └── typescript.lua # LSP, Treesitter, completion
│       └── keymaps/          # Key binding definitions
│           ├── nvimtree.lua  # File tree keymaps
│           └── telescope.lua # Fuzzy finder keymaps
```

## 🔧 First Run

After installing the dotfiles:

1. Open Neovim: `nvim`
2. Lazy.nvim will automatically install all plugins
3. Wait for installation to complete
4. Restart Neovim

## 🎨 Customization

### **Adding Plugins**
1. Create a new file in `lua/plugins/`
2. Return a table with plugin configuration
3. Run `:Lazy sync` to install

Example:
```lua
-- lua/plugins/my-plugin.lua
return {
  "username/plugin-name",
  config = function()
    -- Plugin configuration
  end,
}
```

### **Adding Keymaps**
1. Create or edit files in `lua/keymaps/`
2. Use `vim.keymap.set()` for new bindings

Example:
```lua
-- lua/keymaps/my-keymaps.lua
vim.keymap.set("n", "<leader>w", "<cmd>w<CR>", { desc = "Save file" })
```

### **LSP Configuration**
The configuration includes:
- **TypeScript/JavaScript** support
- **Prettier** formatting
- **ESLint** diagnostics
- **Auto-completion** with LSP sources

## 🔄 Updating

```bash
# Update plugins
nvim +Lazy sync

# Or from command line
nvim --headless "+Lazy! sync" +qa
```

## 🐛 Troubleshooting

### **Plugin Issues**
- Run `:Lazy clean` to remove unused plugins
- Run `:Lazy sync` to reinstall plugins
- Check `:Lazy log` for error messages

### **LSP Issues**
- Run `:LspInfo` to check LSP status
- Run `:LspRestart` to restart language servers
- Install language servers: `:LspInstall <language>`

### **Performance**
- Check `:Lazy profile` for slow plugins
- Use `:Lazy health` to check plugin health
- Disable unused plugins in their configuration files

## 🎯 Philosophy

- **Fast startup** - Lazy loading and minimal configuration
- **Modern Lua** - Uses latest Neovim Lua APIs
- **Modular** - Easy to add, remove, or modify components
- **Developer-focused** - Optimized for coding workflows

---

🧩 Return to [dotfiles root](../README.md) for setup instructions and tool list.
