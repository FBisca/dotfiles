npm() {
  case "$1" in
    ss | show-scripts)
      show_pretty_json "scripts" "\033[1;36m" "package.json" "$2" ;;  # cyan

    sd | show-dependencies)
      show_pretty_json "dependencies" "\033[1;32m" "package.json" "$2" ;;  # green

    sdd | show-dev-dependencies)
      show_pretty_json "devDependencies" "\033[1;33m" "package.json" "$2" ;;  # yellow

    *)
      command npm "$@"
      ;;
  esac
}

