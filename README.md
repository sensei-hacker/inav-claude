# INAV Claude Code Workflow

Claude Code workflow infrastructure for INAV flight controller development using a multi-role AI agent system.

## Overview

This repository provides a structured workflow for using Claude Code to develop INAV firmware and configurator features. It implements a role-based system where different Claude instances take on specific responsibilities (Manager, Developer, Release Manager), communicating through an email-like message passing system.

## Quick Start

### 1. Clone This Repository

```bash
git clone git@github.com:sensei-hacker/inav-claude.git
cd inav-claude
```

### 2. Clone the Required Repositories

This workflow requires the INAV firmware, configurator, and uNAVlib repositories. Clone them into the appropriate directories:

```bash
# Clone INAV firmware
git clone git@github.com:sensei-hacker/inav_unofficial_targets.git inav
# Or use the official repo:
# git clone https://github.com/iNavFlight/inav.git inav

# Clone INAV configurator
git clone git@github.com:sensei-hacker/inav-configurator.git inav-configurator
# Or use the official repo:
# git clone https://github.com/iNavFlight/inav-configurator.git inav-configurator

# Clone uNAVlib (testing library)
git clone https://github.com/your-fork/uNAVlib.git uNAVlib
```

### 3. Start Claude Code

Start Claude from the project root directory:

```bash
claude
```

Claude will read `CLAUDE.local.md` and ask which role you want to work in (Manager, Developer, or Release Manager).

## Roles and Workflow

### Development Manager
- **Directory:** `manager/`
- **Responsibilities:** Project planning, task assignment, progress tracking
- **Read:** `manager/README.md`

### Developer
- **Directory:** `developer/`
- **Responsibilities:** Implementation, testing, code writing
- **Read:** `developer/README.md`
- **Tools:** `test_tools/` contains SITL testing utilities

### Release Manager
- **Directory:** `release-manager/`
- **Responsibilities:** Firmware building, release packaging, distribution
- **Read:** `release-manager/README.md`

### Communication Between Roles

Roles communicate via message files in `inbox/`, `outbox/`, `sent/`, and `inbox-archive/` directories. The `email` skill helps read and manage messages.

See `COMMUNICATION.md` for detailed message formats and workflows.

## The Required Repositories

This workflow is designed to work with three separate repositories:

### inav/
- **Your fork:** https://github.com/sensei-hacker/inav_unofficial_targets
- **Official upstream:** https://github.com/iNavFlight/inav
- **Description:** INAV flight controller firmware (C/C99, embedded systems)
- **License:** GPL

### inav-configurator/
- **Your fork:** https://github.com/sensei-hacker/inav-configurator
- **Official upstream:** https://github.com/iNavFlight/inav-configurator
- **Description:** Desktop configuration GUI (JavaScript/Electron)
- **License:** GPL

### uNAVlib/
- **Description:** Testing and simulation library for UAV development
- **Used by:** Developer test tools in `developer/test_tools/`

**Important:** The `inav/`, `inav-configurator/`, and `uNAVlib/` directories are NOT tracked by this repository. You need to clone them separately as shown above.

## Building INAV Firmware

### Quick Build (Docker - Recommended)
```bash
cd inav
./build.sh MATEKF405SE
```

### List Available Targets
```bash
cd inav
./build.sh valid_targets
```

### SITL (Software In The Loop) for Testing
```bash
cd inav
mkdir -p build_sitl
cd build_sitl
cmake -DSITL=ON ..
make
./inav_SITL
```

The `build-sitl` and `sitl-arm` skills automate SITL building and testing.

## Building INAV Configurator

```bash
cd inav-configurator
npm install
npm start              # Development mode
npm run make           # Build distributable packages
```

## Code Navigation

Both codebases use ctags for quick symbol lookup:

```bash
# Generate tags for firmware (from inav/ directory)
cd inav
ctags -R --fields=+niazS --extras=+q --exclude=lib --exclude=build --exclude=tools --exclude=.git -f tags .

# Generate tags for configurator (from inav-configurator/ directory)
cd inav-configurator
ctags -R --fields=+niazS --extras=+q --exclude=node_modules --exclude=.git --exclude=out --exclude=.vite --exclude=dist -f tags .
```

Use the `/find-symbol` slash command in Claude Code for quick lookups.

See `INDEXING.md` for more details.

## Repository Structure

```
inav-claude/
├── README.md                    # This file
├── CLAUDE.local.md              # Role selection guide (start here)
├── .claude/                     # Root-level Claude settings
│   ├── settings.local.json
│   └── skills/                  # Claude skills (build-sitl, email, etc.)
├── claude/                      # Workflow infrastructure
│   ├── README.md                # Workflow overview
│   ├── COMMUNICATION.md         # Cross-role communication guidelines
│   ├── INDEXING.md              # Code navigation with ctags
│   ├── manager/                 # Development Manager role
│   │   ├── README.md
│   │   ├── CLAUDE.local.md
│   │   └── .claude/settings.local.json
│   ├── developer/               # Developer role
│   │   ├── README.md
│   │   ├── CLAUDE.local.md
│   │   ├── .claude/settings.local.json
│   │   └── test_tools/          # Testing utilities for SITL
│   ├── release-manager/         # Release Manager role
│   │   ├── README.md
│   │   └── download_guide.md
│   ├── projects/                # Project tracking
│   │   └── INDEX.md
│   └── archived_projects/       # Completed project documentation
├── inav/                        # INAV firmware (clone separately)
├── inav-configurator/           # INAV configurator GUI (clone separately)
└── uNAVlib/                     # UAV testing library (clone separately)
```

## Documentation

- **Role Selection:** `CLAUDE.local.md` (start here!)
- **Workflow Overview:** `claude/README.md`
- **Manager Guide:** `claude/manager/README.md`
- **Developer Guide:** `claude/developer/README.md`
- **Release Manager Guide:** `claude/release-manager/README.md`
- **Communication Guide:** `claude/COMMUNICATION.md`
- **Code Navigation:** `claude/INDEXING.md`
- **Project Tracking:** `claude/projects/INDEX.md`

## Claude Code Skills

Custom skills in `.claude/skills/`:
- **build-sitl** - Build INAV SITL firmware
- **sitl-arm** - Arm SITL via MSP for testing
- **email** - Read and manage role messages
- **projects** - View project status
- **communication** - View communication templates

## Testing Tools

Developer role includes test utilities in `claude/developer/test_tools/`:
- `gps_*.py` - GPS navigation testing
- `sitl_arm_test.py` - SITL arming tests
- `msp_debug.py` - MSP protocol debugging
- `UNAVLIB.md` - Testing library documentation

## About INAV

INAV is an open-source flight controller firmware with advanced GPS navigation capabilities for:
- Multirotors (quadcopters, hexacopters, etc.)
- Fixed-wing aircraft and flying wings
- Rovers (ground vehicles)
- Boats (water vehicles)

Key features:
- Waypoint missions (up to 120 waypoints)
- Return-to-home with multiple modes
- Auto-launch for fixed-wing
- Position hold, altitude hold
- Fixed-wing autoland

## Resources

- INAV Official Documentation: https://github.com/iNavFlight/inav/wiki
- INAV Discord: https://discord.gg/peg2hhbYwN
- Claude Code: https://claude.ai/code

## License

This workflow infrastructure is licensed under GPLv2.

The INAV firmware and configurator repositories have their own GPL licenses.

## Contributing

This is a personal workflow repository. For INAV contributions:
- Firmware: https://github.com/iNavFlight/inav
- Configurator: https://github.com/iNavFlight/inav-configurator
