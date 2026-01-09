#!/bin/bash

# Claude Workspace Installation Script
# Usage: ./install.sh [fresh|continue]

set -e

CLAUDE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$CLAUDE_DIR"

echo "=================================="
echo "Claude Workspace Installation"
echo "=================================="
echo ""

# Function to create directory structure
create_directories() {
    echo "Creating directory structure..."

    # Project directories
    mkdir -p projects/active
    mkdir -p projects/backburner
    mkdir -p projects/completed

    # Role directories with email
    for role in manager developer release-manager security-analyst; do
        mkdir -p "$role/email/inbox"
        mkdir -p "$role/email/sent"
        mkdir -p "$role/email/outbox"
        mkdir -p "$role/email/inbox-archive"
    done

    # Developer workspace
    mkdir -p developer/workspace

    # Locks directory
    mkdir -p locks

    echo "✓ Directories created"
}

# Function to clear active content
clear_active_content() {
    echo "Clearing active content..."

    # Clear active/backburner projects (keep completed for reference)
    rm -rf projects/active/* 2>/dev/null || true
    rm -rf projects/backburner/* 2>/dev/null || true

    # Clear all email directories
    for role in manager developer release-manager security-analyst; do
        rm -rf "$role/email/inbox/"* 2>/dev/null || true
        rm -rf "$role/email/sent/"* 2>/dev/null || true
        rm -rf "$role/email/outbox/"* 2>/dev/null || true
        rm -rf "$role/email/inbox-archive/"* 2>/dev/null || true
    done

    # Clear developer workspace
    rm -rf developer/workspace/* 2>/dev/null || true

    # Clear locks
    rm -f locks/*.lock 2>/dev/null || true

    echo "✓ Active content cleared"
}

# Function to show status
show_status() {
    echo ""
    echo "Current Status:"
    echo "---------------"

    active_count=$(find projects/active -maxdepth 1 -type d 2>/dev/null | wc -l)
    active_count=$((active_count - 1))  # Subtract 1 for the directory itself

    completed_count=$(find projects/completed -maxdepth 1 -type d 2>/dev/null | wc -l)
    completed_count=$((completed_count - 1))

    echo "Active projects: $active_count"
    echo "Completed projects: $completed_count"
    echo ""
}

# Main logic
MODE="${1:-}"

if [ -z "$MODE" ]; then
    echo "This script sets up the Claude workspace for INAV development."
    echo ""
    echo "Options:"
    echo "  fresh    - Start with clean projects and emails"
    echo "             (keeps completed projects and examples for reference)"
    echo ""
    echo "  continue - Keep existing projects and emails from previous owner"
    echo "             (useful for continuing sensei's work)"
    echo ""
    read -p "Choose mode [fresh/continue]: " MODE
fi

case "$MODE" in
    fresh)
        echo ""
        echo "Setting up fresh workspace..."
        create_directories
        clear_active_content
        echo ""
        echo "✓ Fresh workspace ready!"
        echo ""
        echo "Next steps:"
        echo "1. Choose your role (manager, developer, etc.)"
        echo "2. Read the role's README.md file"
        echo "3. Check examples/ for templates"
        ;;
    continue)
        echo ""
        echo "Continuing with existing data..."
        create_directories
        echo ""
        echo "✓ Workspace verified!"
        show_status
        echo "Next steps:"
        echo "1. Review existing projects: ls projects/active/"
        echo "2. Check inbox: ls manager/email/inbox/"
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Usage: ./install.sh [fresh|continue]"
        exit 1
        ;;
esac

echo ""
echo "For help, see INSTALL.md"
