// A few generic icons as inline SVG. Recreate the product's own glyphs the same way
// (viewBox 0 0 24 24, sized + colored by prop). Keep them as SVG, not font/emoji.
type P = {size?: number; color: string};

export const ArrowUp = ({size = 14, color}: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 19V5M6 11l6-6 6 6" />
  </svg>
);

export const Sparkle = ({size = 14, color}: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color}>
    <path d="M12 2c.5 4.5 2.5 6.5 7 7-4.5.5-6.5 2.5-7 7-.5-4.5-2.5-6.5-7-7 4.5-.5 6.5-2.5 7-7z" />
  </svg>
);

export const CheckCircle = ({size = 16, color}: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color}>
    <path d="M12 2a10 10 0 100 20 10 10 0 000-20zm-1.2 14.2l-4-4 1.4-1.4 2.6 2.6 5.6-5.6L17.8 9l-7 7.2z" />
  </svg>
);

// A macOS-style pointer, for a click/hover accent.
export const Cursor = ({size = 26}: {size?: number}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.35))'}}>
    <path d="M5 2l14 8.5-6 1.4-1.6 6.6L5 2z" fill="#fff" stroke="#1A1A1A" strokeWidth="1.2" strokeLinejoin="round" />
  </svg>
);

// A spinning ring - pass the current frame to rotate it.
export const Spinner = ({size = 16, color, frame}: P & {frame: number}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{transform: `rotate(${frame * 12}deg)`}}>
    <circle cx="12" cy="12" r="9" fill="none" stroke={color} strokeOpacity={0.2} strokeWidth={2.6} />
    <path d="M12 3a9 9 0 019 9" fill="none" stroke={color} strokeWidth={2.6} strokeLinecap="round" />
  </svg>
);
