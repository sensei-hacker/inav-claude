#!/usr/bin/env node
/*
 * Brief: Connect to an INAV Configurator CDP page target and evaluate one JS
 *        expression in the renderer, printing the JSON result.
 *
 * Usage:  node cdp_eval.mjs <webSocketDebuggerUrl> <expression | ->
 *         Pass `-` as the expression to read it from stdin.
 *
 * Example:
 *   WS_URL=$(curl -s http://localhost:9222/json/list | jq -r '.[0].webSocketDebuggerUrl')
 *   node cdp_eval.mjs "$WS_URL" "document.title"
 *   echo "MSP.promise(1, 1)" | node cdp_eval.mjs "$WS_URL" -
 *
 * What problem this solves:
 *   Driving the Configurator's renderer over Chrome DevTools Protocol requires
 *   a WebSocket client that sends Runtime.evaluate and awaits the JSON result.
 *   This helper removes that boilerplate: it connects to a single target's
 *   webSocketDebuggerUrl, evaluates the expression with awaitPromise,
 *   returnByValue, and userGesture, prints the resulting value as JSON, and
 *   exits non-zero on CDP error, renderer exception, or a 20s timeout. It was
 *   used to reproduce the MSP.promise() hang live — driving
 *   import('/js/msp.js'), poisoning MSP.parseFailures, and observing the
 *   promise never settling (buggy) vs rejecting (fixed).
 *
 * When to use it:
 *   For configurator/UI-only changes with no unit-testable seam, per
 *   CRITICAL-BEFORE-TEST.md — drive an already-running Configurator (dev mode
 *   auto-opens CDP on CDP_PORT, default 9222) via CDP. Use this for a quick
 *   one-shot Runtime.evaluate in the renderer (state inspection, poisoning
 *   globals, observing async promise settlement) instead of writing a full
 *   Python CDP script. It does NOT open a page or drive the UI; for that, use
 *   configurator_cdp_test.py / tab_sweep_cdp.py or the Chrome DevTools MCP.
 */
import { readFileSync } from 'node:fs';

const usage = () => {
    console.error('usage: node cdp_eval.mjs <webSocketDebuggerUrl> <expression | ->');
    console.error('  expression  JS expression to Runtime.evaluate in the renderer');
    console.error('  -           read the expression from stdin');
    process.exit(2);
};

if (process.argv.includes('--help') || process.argv.includes('-h')) {
    console.log([
        'cdp_eval.mjs — evaluate one JS expression in a running INAV Configurator via CDP',
        '',
        'Usage:',
        '  node cdp_eval.mjs <webSocketDebuggerUrl> <expression | ->',
        '',
        'Arguments:',
        '  webSocketDebuggerUrl  CDP page target, e.g. from:',
        '                        curl -s http://localhost:9222/json/list | jq -r \'.[0].webSocketDebuggerUrl\'',
        '  expression            JS expression to evaluate (awaitPromise/returnByValue/userGesture)',
        '  -                     read the expression from stdin',
        '',
        'Examples:',
        '  WS_URL=$(curl -s http://localhost:9222/json/list | jq -r \'.[0].webSocketDebuggerUrl\')',
        '  node cdp_eval.mjs "$WS_URL" "document.title"',
        '  echo "MSP.promise(1, 1)" | node cdp_eval.mjs "$WS_URL" -',
        '',
        'Exit codes: 0 success (JSON result printed to stdout), 1 CDP error/',
        'exception/timeout, 2 usage error.',
    ].join('\n'));
    process.exit(0);
}

const wsUrl = process.argv[2];
let expr = process.argv[3];
if (expr === '-') expr = readFileSync(0, 'utf8');
if (!wsUrl || !expr) usage();

const ws = new WebSocket(wsUrl);
let settled = false;
const finish = (code) => { if (settled) return; settled = true; try { ws.close(); } catch {} setTimeout(() => process.exit(code), 20); };

ws.onopen = () => ws.send(JSON.stringify({ id: 1, method: 'Runtime.evaluate',
    params: { expression: expr, awaitPromise: true, returnByValue: true, userGesture: true } }));

ws.onmessage = (ev) => {
    let msg; try { msg = JSON.parse(ev.data); } catch { return; }
    if (msg.id !== 1) return;
    if (msg.error) { console.error('CDP error:', JSON.stringify(msg.error)); finish(1); return; }
    if (msg.result && msg.result.exceptionDetails) { console.error('EXCEPTION:', JSON.stringify(msg.result.exceptionDetails, null, 2)); finish(1); return; }
    console.log(JSON.stringify(msg.result && msg.result.result, null, 2));
    finish(0);
};
ws.onerror = (e) => { console.error('WS error:', e && e.message ? e.message : String(e)); finish(1); };
setTimeout(() => { console.error('timeout waiting for CDP response'); finish(1); }, 20000);
