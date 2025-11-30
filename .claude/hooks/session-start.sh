#!/bin/bash
# SessionStart hook - Ask user for role selection
# Outputs JSON with systemMessage that will be shown to the user

cat <<'EOF'
{
  "systemMessage": "Which role would you like me to have today - Manager, Developer, or Release Manager?"
}
EOF

exit 0
