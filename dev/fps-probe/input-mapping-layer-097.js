/* Story 097 controller-mapping-layer (Session 42). Plain JS, no build,
 * no dependency. Usable in a browser (attaches to window) and in node
 * (module.exports) without DOM access.
 *
 * Standard layout intents (binding intent-resolution table):
 *   left stick  (axes[0], axes[1]) -> move intent  { moveX, moveY }
 *   right stick (axes[2], axes[3]) -> look intent  { lookDX, lookDY }
 *   trigger RT (buttons[7], value/pressed) or primary button (buttons[0])
 *     -> fire intent { fire }
 * The layer resolves intents to the Story 091 slice inputs: WASD-equivalent
 * move, Pointer Lock (or synthetic) look deltas, click-to-shoot fire.
 * Gamepad polls on this box are synthetic fixtures only (no hardware);
 * they prove the table structurally and nothing about hardware.
 * Marker: mapping097.
 */
'use strict';

var INTENT_TABLE = {
  move: { source: 'left stick', axes: [0, 1], intent: ['moveX', 'moveY'] },
  look: { source: 'right stick', axes: [2, 3], intent: ['lookDX', 'lookDY'] },
  fire: { source: 'trigger RT or primary button',
    buttons: [7, 0], intent: ['fire'] }
};

var STICK_DEADZONE = 0.15;
var LOOK_SCALE = 40;
var TRIGGER_THRESHOLD = 0.3;

function padAxis(v) {
  var n = (+v) || 0;
  if (Math.abs(n) < STICK_DEADZONE) return 0;
  if (n > 1) return 1;
  if (n < -1) return -1;
  return n;
}

function padButton(b) {
  if (!b) return false;
  if (typeof b === 'number') return b > TRIGGER_THRESHOLD;
  return !!b.pressed || ((+b.value) || 0) > TRIGGER_THRESHOLD;
}

/* resolveGamepadPoll(poll): poll is a Gamepad-like frame
 * { axes: [x0,y0,x1,y1], buttons: [{pressed, value} ...] }.
 * Returns intent { moveX, moveY, lookDX, lookDY, fire }.
 * Synthetic fixture frames only on this box; labeled structural. */
function resolveGamepadPoll(poll) {
  var axes = (poll && poll.axes) || [];
  var buttons = (poll && poll.buttons) || [];
  return {
    moveX: padAxis(axes[0]),
    moveY: padAxis(axes[1]),
    lookDX: padAxis(axes[2]) * LOOK_SCALE,
    lookDY: padAxis(axes[3]) * LOOK_SCALE,
    fire: padButton(buttons[7]) || padButton(buttons[0])
  };
}

/* resolveKeyboardIntent(kb): kb is
 * { keys: {KeyW,KeyA,KeyS,KeyD booleans}, lookDX, lookDY, click }.
 * Returns the same intent shape, proven end to end in the harness. */
function resolveKeyboardIntent(kb) {
  var keys = (kb && kb.keys) || {};
  var fwd = (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0);
  var strafe = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0);
  return {
    moveX: strafe,
    moveY: fwd,
    lookDX: ((kb && kb.lookDX) || 0),
    lookDY: ((kb && kb.lookDY) || 0),
    fire: !!((kb && kb.click))
  };
}

var Mapping097 = {
  INTENT_TABLE: INTENT_TABLE,
  STICK_DEADZONE: STICK_DEADZONE,
  LOOK_SCALE: LOOK_SCALE,
  TRIGGER_THRESHOLD: TRIGGER_THRESHOLD,
  resolveGamepadPoll: resolveGamepadPoll,
  resolveKeyboardIntent: resolveKeyboardIntent
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = Mapping097;
}
if (typeof window !== 'undefined') {
  window.Mapping097 = Mapping097;
}
