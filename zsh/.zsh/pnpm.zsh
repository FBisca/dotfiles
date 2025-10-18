# PNPM home directory
export PNPM_HOME="${HOME}/Library/pnpm"

# Add PNPM to PATH if it exists and isn't already in PATH
if [[ -d "$PNPM_HOME" ]]; then
  case ":$PATH:" in
    *":$PNPM_HOME:"*) ;;
    *) export PATH="$PNPM_HOME:$PATH" ;;
  esac
fi

# Function to show pnpm scripts in a pretty format
pnpm() {
  case "$1" in
    ss | show-scripts)
      if [[ -f "package.json" ]]; then
        echo "\033[1;36m📜 Available Scripts:\033[0m"
        jq -r '.scripts | to_entries[] | "  \033[1;32m\(.key)\033[0m: \(.value)"' package.json 2>/dev/null || echo "  No scripts found or jq not available"
      else
        echo "No package.json found in current directory"
      fi
      ;;
    sd | show-dependencies)
      if [[ -f "package.json" ]]; then
        echo "\033[1;32m📦 Dependencies:\033[0m"
        jq -r '.dependencies | to_entries[] | "  \033[1;32m\(.key)\033[0m: \(.value)"' package.json 2>/dev/null || echo "  No dependencies found or jq not available"
      else
        echo "No package.json found in current directory"
      fi
      ;;
    sdd | show-dev-dependencies)
      if [[ -f "package.json" ]]; then
        echo "\033[1;33m🛠️  Dev Dependencies:\033[0m"
        jq -r '.devDependencies | to_entries[] | "  \033[1;33m\(.key)\033[0m: \(.value)"' package.json 2>/dev/null || echo "  No dev dependencies found or jq not available"
      else
        echo "No package.json found in current directory"
      fi
      ;;
    *)
      command pnpm "$@"
      ;;
  esac
}
