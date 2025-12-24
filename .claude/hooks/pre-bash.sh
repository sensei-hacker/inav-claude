#!/bin/bash

# PreToolUse hook for Bash commands
# Checks for git commit and reminds Claude not to mention itself

LOG_FILE="/home/raymorris/Documents/planes/inavflight/.claude/hooks/pre-bash.log"

# Read tool input from stdin
TOOL_INPUT=$(cat)

# Log the invocation
echo "$(date '+%Y-%m-%d %H:%M:%S') - Bash hook triggered" >> "$LOG_FILE"
echo "  Input: $TOOL_INPUT" >> "$LOG_FILE"

# Check if this is a git commit command
if echo "$TOOL_INPUT" | grep -q '"command".*git commit'; then
    echo "  -> Detected git commit, adding reminder" >> "$LOG_FILE"
    cat <<'EOF'
{
  "additionalContext": "IMPORTANT: Do not mention Claude, AI, or that this commit was AI-generated in the commit message. Write the commit message as if a human developer wrote it. Also, be sure to use your git-workflow and create-pr skills when doing the first commit on a new task, or when creating a pull request."
}
EOF
elif echo "$TOOL_INPUT" | egrep -q '"command".*git push.*(maintenance|master)'; then
cat <<'EOF'
{
  "additionalContext": "IMPORTANT: Do NOT push to a version brach (maintenance-9.x, maintenance-10.x) or to master (except for inavwiki). Use your create-pr skill with a feature branch."
}
EOF

elif echo "$TOOL_INPUT" | egrep -q '"command".*git push.*force'; then
cat <<'EOF'
{
  "additionalContext": "IMPORTANT: Do NOT force push! That will break public history!"
}
EOF
else
    echo "  -> Not a git commit, allowing" >> "$LOG_FILE"
fi

exit 0
