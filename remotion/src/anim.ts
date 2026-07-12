// Reusable animation helpers. All times are in frames. These are product-agnostic -
// use them verbatim. See references/techniques.md for how each is used.
import {interpolate, spring} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const fade = (frame: number, start: number, dur = 10) =>
  interpolate(frame, [start, start + dur], [0, 1], clamp);

export const fadeOut = (frame: number, start: number, dur = 10) =>
  interpolate(frame, [start, start + dur], [1, 0], clamp);

// Fade in at inAt, hold, fade out ending at outAt. For lower-third captions.
export const inOut = (frame: number, inAt: number, outAt: number, d = 8) =>
  interpolate(frame, [inAt, inAt + d, outAt - d, outAt], [0, 1, 1, 0], clamp);

// Spring rise: returns {opacity, y} for a settle-up entrance (apply as opacity + translateY).
export const riseIn = (frame: number, fps: number, start: number, dist = 16) => {
  const s = spring({frame: frame - start, fps, config: {damping: 200, mass: 0.7}});
  return {opacity: Math.min(1, s * 1.2), y: (1 - s) * dist};
};

// Characters of `text` revealed by `frame`, typed from `start` at cps chars/sec.
export const typed = (text: string, frame: number, start: number, cps: number, fps: number) =>
  text.slice(0, Math.floor(Math.max(0, frame - start) * (cps / fps)));

export const typedDone = (text: string, frame: number, start: number, cps: number, fps: number) =>
  Math.max(0, frame - start) * (cps / fps) >= text.length;

// Blinking caret (0/1) while typing.
export const caret = (frame: number) => (Math.floor(frame / 15) % 2 === 0 ? 1 : 0);

// Show step N of a working sequence, based on elapsed frames.
export const cycleStep = (steps: string[], frame: number, start: number, per: number) =>
  steps[Math.max(0, Math.min(steps.length - 1, Math.floor((frame - start) / per)))];
