# Debugging Scripts and CLI Tools

Lessons learned while developing the FC profiling automation.

## Problem: Missing Error Messages

### Issue
When running Python scripts that call subprocesses, errors were hidden because:
- `subprocess.run(capture_output=True)` captures stderr but doesn't print it
- Scripts failed silently without visible error messages

### Solution
Always print stderr from subprocesses:

```python
result = subprocess.run(
    ['some-command', 'arg1'],
    capture_output=True,
    text=True,
    timeout=60
)

# ALWAYS print stderr if present
if result.stderr:
    print(f"Command stderr: {result.stderr[:500]}")

# Also print stdout if command failed
if result.returncode != 0:
    print(f"Command failed with code {result.returncode}")
    print(f"stdout: {result.stdout[:300]}")
```

### Example: DFU Flashing

**Before (silent failures):**
```python
result = subprocess.run(['dfu-util', '-d', '2e3c:df11', ...],
                        capture_output=True)
if 'Download done' in result.stdout:
    return True
# Fails silently - we never see "No DFU device found"
```

**After (visible errors):**
```python
result = subprocess.run(['dfu-util', '-d', '2e3c:df11', ...],
                        capture_output=True, text=True)

if result.stderr:
    print(f"DFU stderr: {result.stderr[:500]}")

if 'Download done' in result.stdout:
    return True
else:
    print(f"DFU output: {result.stdout[:300]}")
    # Now we see: "No DFU capable USB device available"
```

## Problem: FC CLI Already in CLI Mode

### Issue
The `fc-cli.py` script sends `####\r\n` to enter CLI mode and waits for the string "CLI" in the response.

**Problem:** If the FC is already in CLI mode (e.g., from a previous command), it just responds with `#` (the prompt), not the full "CLI" string.

**Result:** Script times out waiting for "CLI" that never appears.

### Solution
Accept either "CLI" (fresh entry) or "#" (already in CLI):

```python
# Before
if b'CLI' in received_data:
    return True

# After
if b'CLI' in received_data or b'#' in received_data:
    return True
```

**Location:** `.claude/skills/flash-firmware-dfu/fc-cli.py` line 82

### Why This Happens
When you flash firmware with an early `return` statement (for profiling), the FC may not fully initialize. It stays in a semi-CLI state where:
- It accepts CLI commands
- But doesn't send the full "CLI" banner
- Just shows the `#` prompt

## Running CLI Commands on FC

### Using fc-cli.py

**Built-in commands:**
```bash
# Reboot to DFU mode
.claude/skills/flash-firmware-dfu/fc-cli.py dfu

# Show task execution times
.claude/skills/flash-firmware-dfu/fc-cli.py tasks

# Show firmware version
.claude/skills/flash-firmware-dfu/fc-cli.py version

# Show FC status
.claude/skills/flash-firmware-dfu/fc-cli.py status
```

**Custom commands:**
```bash
# Any CLI command
.claude/skills/flash-firmware-dfu/fc-cli.py "get gyro_lpf1_static_hz"
.claude/skills/flash-firmware-dfu/fc-cli.py "diff"
.claude/skills/flash-firmware-dfu/fc-cli.py "dump"
```

**With custom serial port:**
```bash
.claude/skills/flash-firmware-dfu/fc-cli.py tasks /dev/ttyUSB0
```

### How fc-cli.py Works

1. Opens serial port (default 115200 baud)
2. Sends `####\r\n` to enter CLI mode
3. Waits for "CLI" or "#" in response (2 second timeout)
4. Sends your command
5. Reads response (1 second timeout after last data)
6. Closes connection

### Troubleshooting CLI Commands

**Timeout entering CLI:**
```bash
$ fc-cli.py tasks
Opening serial port: /dev/ttyACM0
Entering CLI mode...
Waiting for CLI prompt...
✗ ERROR: Timeout waiting for CLI prompt
Received: ####
```

**Fix:** FC already in CLI mode, update fc-cli.py to accept `#` prompt (see above).

**No serial device:**
```bash
$ fc-cli.py tasks /dev/ttyACM0
✗ ERROR: Serial port error: [Errno 2] No such file or directory
```

**Fix:** Check device exists: `ls -la /dev/ttyACM*` or `ls -la /dev/ttyUSB*`

**Permission denied:**
```bash
✗ ERROR: Serial port error: [Errno 13] Permission denied: '/dev/ttyACM0'
```

**Fix:** Add user to dialout group:
```bash
sudo usermod -a -G dialout $USER
# Log out and back in for group change to take effect
```

## Python Script Debugging Tips

### Always Use Unbuffered Output

When running Python scripts in background or with redirects:

```bash
# BAD - output may be buffered and not appear
python3 script.py > log.txt

# GOOD - unbuffered output
python3 -u script.py > log.txt
stdbuf -o0 python3 script.py > log.txt
```

### Redirect Both stdout and stderr

```bash
# Capture both streams
python3 script.py > log.txt 2>&1

# Or separately
python3 script.py > stdout.log 2> stderr.log
```

### Use Print for Debugging

In Python scripts that call subprocesses:

```python
# Print before subprocess calls
print(f"Running command: {command}")
sys.stdout.flush()  # Force flush if buffering

result = subprocess.run(...)

# Print after
print(f"Command completed: return code {result.returncode}")
```

### Test Incrementally

Don't write a huge script and run it. Test each part:

```python
# Test just the CLI connection
cli = FlightControllerCLI('/dev/ttyACM0')
if cli.enter_cli_mode():
    print("✓ CLI works")

# Test just sending a command
response = cli.send_command('tasks')
print(response)

# Then test the full workflow
```

## Subprocess Error Handling Checklist

When calling external commands:

- [ ] Capture both stdout and stderr (`capture_output=True`)
- [ ] Print stderr if present
- [ ] Print stdout if command failed
- [ ] Handle TimeoutExpired exception
- [ ] Handle FileNotFoundError (command not found)
- [ ] Check return code
- [ ] Log what command you're running

**Template:**
```python
def run_command_safely(cmd, timeout=30):
    """Run command with proper error handling."""
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # Print stderr if present
        if result.stderr:
            print(f"stderr: {result.stderr}")

        # Check return code
        if result.returncode != 0:
            print(f"Command failed with code {result.returncode}")
            print(f"stdout: {result.stdout}")
            return None

        return result.stdout

    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout}s")
        return None
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Summary

**Key Lessons:**
1. Never discard stderr - always print it
2. FC CLI can respond with just "#" when already in CLI mode
3. Use unbuffered Python output (`-u`) for real-time logs
4. Test scripts incrementally, not all at once
5. Print what commands you're running before running them
6. Handle subprocess exceptions properly

**Files Updated:**
- `.claude/skills/flash-firmware-dfu/fc-cli.py` - Accept "#" prompt
- `claude/developer/profile-fc.py` - Print all subprocess stderr
