#!/usr/bin/env node
/*
 * Brief: Verify (on a live, real-hardware Configurator connection) that a
 *        "dropped MSP write" guard actually suppresses a chained completion
 *        callback, with independent positive proof the drop condition was
 *        really triggered - not just silence.
 *
 * Usage:
 *   node verify_cli_lock_write_guard.mjs <webSocketDebuggerUrl> \
 *       --code <MSPCodes key, e.g. MSP2_INAV_SET_LED_STRIP_CONFIG_EX> \
 *       --payload "[0,0,0,0,0,0]" \
 *       --guarded-call "mspHelper.sendLedStripConfig(cb, new Set([0]))" \
 *       [--helper-module /js/msp/MSPHelper.js] \
 *       [--wait-ms 7000]
 *
 * Prerequisite (you must do this manually first, via the real UI - NOT by
 * poking CONFIGURATOR.cliActive from the console):
 *   1. Connect the Configurator to a real FC.
 *   2. Click into the CLI tab in the actual UI and confirm (screenshot) the
 *      "CLI mode detected" log line and a live `#` prompt. This is what
 *      genuinely locks the MSP send queue - `CONFIGURATOR.cliActive` flips
 *      true as a side effect of tabs/cli.js's real entry code.
 *   3. THEN run this script against that same page's CDP ws url.
 *   4. Afterwards, click "Exit" in the CLI tab UI to cleanly leave CLI mode
 *      (this sends `exit` to the FC and triggers a real reboot/reconnect -
 *      expected; reconnect afterwards).
 *
 * What problem this solves:
 *   Several MSP write chains (sendLedStripConfig, sendLedStripColors,
 *   sendLedStripModeColors, setSetting, OSD.saveItem, ...) call
 *   MSP.send_message() with a plain completion callback. When the send
 *   queue gives up on a write (e.g. because CONFIGURATOR.cliActive is true
 *   and msp.js's _enqueue() has no way to ever land the message), it invokes
 *   that callback with the literal `false` instead of a response. Unguarded
 *   chains treat that as success and advance/complete anyway. Fixes wrap the
 *   callback (e.g. guardMspCallback() in js/mspWriteOutcome.js) to skip
 *   firing when called with `false`.
 *
 *   A live/CDP test that just calls the guarded function and observes "the
 *   callback didn't fire" is NOT trustworthy on its own (see
 *   claude/developer/guides/CRITICAL-BEFORE-TEST.md, "Absence of evidence is
 *   not evidence of absence") - silence is equally consistent with "the fix
 *   works" and "this test never actually touched live state". This script
 *   makes the result trustworthy by ALSO calling the raw, unwrapped
 *   MSP.send_message() for the same MSP code under the identical live
 *   condition, proving the drop really fires (and capturing its real
 *   timing), before trusting that the guarded call's silence means anything.
 *
 * Known timing quirk (see js/msp.js _enqueue()): when CONFIGURATOR.cliActive
 * is true, the retry branch's condition includes `!CONFIGURATOR.cliActive`,
 * which is false - so it skips retries entirely and calls onFinish(false)
 * SYNCHRONOUSLY (~0ms), not after any delay. Don't assume you need a long
 * wait for the raw probe; the guarded probe still needs a generous wait
 * (default 7s) to be a meaningful "did NOT fire" result.
 *
 * DANGER - real CLI mode + a Vite full-reload can strand the FC: if the
 * Configurator's renderer does a full page reload (e.g. Vite HMR reloading
 * a deep dependency) while CONFIGURATOR.cliActive is genuinely true, the
 * clean "send exit on tab leave" logic in tabs/cli.js never runs, and the
 * physical FC is left sitting at a raw CLI `#` prompt with no owner. Every
 * later MSP reconnect attempt then fails with "No configuration received
 * within 10 seconds" until you recover it - open the serial port directly
 * (e.g. pyserial) and write `exit\r\n` to it, wait ~5s for the FC's own
 * reboot, then reconnect normally. Don't assume the FC/wiring is broken.
 *
 * Exit codes: 0 = PASS (raw drop confirmed fast, guarded call never fired).
 *             1 = FAIL or INCONCLUSIVE (see printed verdict for which).
 */
import { readFileSync } from 'node:fs';

function parseArgs(argv) {
    const args = { waitMs: 7000, helperModule: '/js/msp/MSPHelper.js' };
    const positional = [];
    for (let i = 0; i < argv.length; i++) {
        const a = argv[i];
        if (a === '--code') args.code = argv[++i];
        else if (a === '--payload') args.payload = argv[++i];
        else if (a === '--guarded-call') args.guardedCall = argv[++i];
        else if (a === '--helper-module') args.helperModule = argv[++i];
        else if (a === '--wait-ms') args.waitMs = parseInt(argv[++i], 10);
        else if (a === '--help' || a === '-h') args.help = true;
        else positional.push(a);
    }
    args.wsUrl = positional[0];
    return args;
}

const args = parseArgs(process.argv.slice(2));

if (args.help || !args.wsUrl || !args.code || !args.payload || !args.guardedCall) {
    console.log([
        'verify_cli_lock_write_guard.mjs - prove a dropped-MSP-write guard works, on real hardware',
        '',
        'Usage:',
        '  node verify_cli_lock_write_guard.mjs <webSocketDebuggerUrl> \\',
        '      --code <MSPCodes key> --payload "<JSON array>" \\',
        '      --guarded-call "<JS expr calling the helper fn with (cb, ...)>" \\',
        '      [--helper-module /js/msp/MSPHelper.js] [--wait-ms 7000]',
        '',
        'Example:',
        '  WS_URL=$(curl -s http://localhost:9222/json/list | jq -r \'.[] | select(.title=="INAV Configurator").webSocketDebuggerUrl\')',
        '  node verify_cli_lock_write_guard.mjs "$WS_URL" \\',
        '      --code MSP2_INAV_SET_LED_STRIP_CONFIG_EX --payload "[0,0,0,0,0,0]" \\',
        '      --guarded-call "mspHelper.sendLedStripConfig(cb, new Set([0]))"',
        '',
        'IMPORTANT: you must have already clicked into the real CLI tab in the',
        'UI (not console-set CONFIGURATOR.cliActive) before running this - it',
        'aborts loudly if cliActive is not genuinely true.',
    ].join('\n'));
    process.exit(args.help ? 0 : 2);
}

const payload = JSON.parse(args.payload);

const script = `
(async () => {
  const cfgMod = await import('/js/data_storage.js');
  const CONFIGURATOR = cfgMod.default;
  if (!CONFIGURATOR.cliActive) {
    return { aborted: true, reason: 'CONFIGURATOR.cliActive is not true - click into the real CLI tab in the UI first. Refusing to run: a console-set flag would not prove the queue is genuinely locked.' };
  }

  const mspMod = await import('/js/msp.js');
  const MSP = mspMod.default || mspMod.MSP;
  const codesMod = await import('/js/msp/MSPCodes.js');
  const MSPCodes = codesMod.default || codesMod.MSPCodes;
  const helperMod = await import(${JSON.stringify(args.helperModule)});
  const mspHelper = helperMod.default;

  if (!(${JSON.stringify(args.code)} in MSPCodes)) {
    return { aborted: true, reason: 'Unknown MSPCodes key: ${args.code}' };
  }
  const code = MSPCodes[${JSON.stringify(args.code)}];

  // --- Raw probe: unwrapped MSP.send_message(), proves the drop is real ---
  const rawStart = performance.now();
  let rawArg = 'NEVER_CALLED_WITHIN_WAIT';
  let rawMs = null;
  await new Promise((resolve) => {
    MSP.send_message(code, ${JSON.stringify(payload)}, false, function (result) {
      rawArg = result;
      rawMs = performance.now() - rawStart;
      resolve();
    });
    setTimeout(resolve, ${args.waitMs});
  });

  // --- Guarded probe: the real helper call chain under test ---
  const guardedStart = performance.now();
  let guardedFired = false;
  let guardedMs = null;
  let guardedArg = null;
  await new Promise((resolve) => {
    const cb = (arg) => {
      guardedFired = true;
      guardedMs = performance.now() - guardedStart;
      guardedArg = arg;
      resolve();
    };
    try {
      (${args.guardedCall});
    } catch (e) {
      resolve({ threw: String(e && e.stack || e) });
      return;
    }
    setTimeout(resolve, ${args.waitMs});
  });

  return {
    aborted: false,
    cliActive: CONFIGURATOR.cliActive,
    rawArg: JSON.stringify(rawArg),
    rawFiredAtMs: rawMs,
    guardedFired,
    guardedFiredAtMs: guardedMs,
    guardedArg: JSON.stringify(guardedArg),
  };
})()
`;

const ws = new WebSocket(args.wsUrl);
let settled = false;
const finish = (code) => { if (settled) return; settled = true; try { ws.close(); } catch {} setTimeout(() => process.exit(code), 20); };

ws.onopen = () => ws.send(JSON.stringify({ id: 1, method: 'Runtime.evaluate',
    params: { expression: script, awaitPromise: true, returnByValue: true, userGesture: true } }));

ws.onmessage = (ev) => {
    let msg; try { msg = JSON.parse(ev.data); } catch { return; }
    if (msg.id !== 1) return;
    if (msg.error) { console.error('CDP error:', JSON.stringify(msg.error)); finish(1); return; }
    if (msg.result && msg.result.exceptionDetails) { console.error('EXCEPTION:', JSON.stringify(msg.result.exceptionDetails, null, 2)); finish(1); return; }
    const r = msg.result && msg.result.result && msg.result.result.value;
    console.log(JSON.stringify(r, null, 2));

    if (!r || r.aborted) {
        console.error('\nINCONCLUSIVE:', (r && r.reason) || 'no result');
        finish(1);
        return;
    }

    const rawDropConfirmed = r.rawArg === 'false';
    if (!rawDropConfirmed) {
        console.error('\nINCONCLUSIVE: the raw, unwrapped send_message() did not receive the literal `false` drop signal.');
        console.error('This means the CLI-lock condition did not actually trigger a drop for this MSP code right now -');
        console.error('a "guarded callback never fired" result below would NOT be meaningful evidence of anything.');
        finish(1);
        return;
    }

    if (r.guardedFired) {
        console.error('\nFAIL: the guarded call\'s callback DID fire (arg=' + r.guardedArg + ') despite a confirmed dropped write.');
        console.error('The guard is either not wired up, not loaded (check for stale JS), or not checking for the right sentinel.');
        finish(1);
        return;
    }

    console.log('\nPASS: raw send_message() confirmed a real dropped write (arg=false @ ' + r.rawFiredAtMs.toFixed(1) +
        'ms), and the guarded call\'s callback correctly did NOT fire within ' + args.waitMs + 'ms.');
    finish(0);
};
ws.onerror = (e) => { console.error('WS error:', e && e.message ? e.message : String(e)); finish(1); };
setTimeout(() => { console.error('timeout waiting for CDP response'); finish(1); }, args.waitMs + 20000);
