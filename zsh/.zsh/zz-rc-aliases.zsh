# Ensure rc aliases take precedence over system tools
# This must load after mise to override its PATH modifications
export PATH="$HOME/.local/bin:$PATH"

# Dynamic rc aliases based on directory configs
eval "$(rc alias-init)"
