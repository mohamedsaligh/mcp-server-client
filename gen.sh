#!/bin/sh

REPO_DIR="backend/db/repository"
mkdir -p $REPO_DIR

# File list
FILES=("user_repo.py" "prompt_context_repo.py" "llm_api_repo.py" "mcp_server_repo.py" "prompt_log_repo.py")

# Create empty repo files
for file in "${FILES[@]}"; do
    touch "$REPO_DIR/$file"
done

echo "✅ Repository files created:"
printf '%s\n' "${FILES[@]}"
