#!/bin/bash

# Dotfiles Installation Script for macOS ARM
# This script installs all dotfiles using GNU Stow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS."
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "README.md" ]] || [[ ! -d ".git" ]]; then
    print_error "Please run this script from the dotfiles directory."
    exit 1
fi

# Check if stow is installed
if ! command -v stow &> /dev/null; then
    print_error "GNU Stow is not installed. Please install it first:"
    echo "  brew install stow"
    exit 1
fi

print_status "Installing dotfiles with GNU Stow..."

# List of modules to install
MODULES=(
    "git"
    "zsh" 
    "nvim"
    "mise"
    "gh"
    "kitty"
    "wezterm"
    "fzf"
    "env"
    "slack"
)

# Install each module
for module in "${MODULES[@]}"; do
    if [[ -d "$module" ]]; then
        print_status "Installing $module..."
        if stow "$module"; then
            print_success "$module installed successfully"
        else
            print_error "Failed to install $module"
            exit 1
        fi
    else
        print_warning "Module $module not found, skipping..."
    fi
done

print_success "All dotfiles installed successfully!"
print_status "Next steps:"
echo "  1. Restart your terminal or run: source ~/.zshrc"
echo "  2. Install Oh My Zsh if not already installed:"
echo "     sh -c \"\$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\""
echo "  3. Install mise if not already installed:"
echo "     curl https://mise.jdx.dev/install.sh | sh"
echo "  4. Install tools with mise:"
echo "     mise install"
echo "  5. Authenticate with GitHub CLI:"
echo "     gh auth login"
echo "  6. Install Nerd Fonts:"
echo "     brew install --cask font-fira-code-nerd-font"
echo "  7. Install additional tools:"
echo "     brew install git gh fzf fd ripgrep bat eza jq"
