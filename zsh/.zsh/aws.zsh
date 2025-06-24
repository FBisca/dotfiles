# ~/.zsh/aws.zsh

aws-load-credentials() {
  local profile="${1:-sdlc}"
  local format="${2:-env}"

  if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Aborting."
    return 1
  fi

  echo "🔐 Loading AWS credentials for profile: $profile (format: $format)"
  source <(aws configure export-credentials --profile "$profile" --format "$format")

  if [[ -n "$AWS_ACCESS_KEY_ID" ]]; then
    echo "✅ AWS credentials for profile '${profile}' loaded successfully."
  else
    echo "⚠️  Warning: Credentials not found or failed to load."
    return 1
  fi
}

