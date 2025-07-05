# 📦 mise Configuration

This directory contains configuration for [`mise`](https://mise.jdx.dev/), a fast and modern runtime manager that replaces tools like `asdf`, `pyenv`, `nvm`, and others.

## 🧠 What This Is

✅ **Fast**: Written in Rust, significantly faster than traditional runtime managers  
🧠 **Unified**: Single tool for managing Node.js, Python, Ruby, Go, and more  
🧩 **Compatible**: Drop-in replacement for `asdf` with better performance  
🔧 **Modern**: Built-in support for tools, plugins, and global configuration

## ✅ Assumptions

- You have `mise` installed. If not, install it from the [official installation page](https://mise.jdx.dev/getting-started.html#installation)
- You're using a shell that supports mise (zsh, bash, fish, etc.)

## ⚡ Performance

mise is significantly faster than traditional runtime managers:

- **Cold start**: ~10ms vs ~200ms for asdf
- **Tool installation**: Parallel downloads and caching
- **Version switching**: Instant symlink updates

## 🔄 Migration from asdf

If you're coming from `asdf`, mise provides full compatibility:

```bash
# Your existing .tool-versions files work automatically
mise install  # Reads .tool-versions and installs versions

# Or migrate to .mise.toml for better performance
mise init
```

---

🧩 Return to [dotfiles root](../README.md) for setup instructions and tool list.
