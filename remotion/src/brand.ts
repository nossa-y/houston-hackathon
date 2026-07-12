// Houston's real design tokens - lifted verbatim from houston/static/index.html.
export const BRAND = {
  bg: '#070b12',
  panel: '#0d1420',
  panel2: '#111a29',
  line: '#1c2940',
  text: '#dbe7f5',
  dim: '#6b7f9c',
  green: '#34d399',
  red: '#fb7185',
  amber: '#fbbf24',
  cyan: '#67e8f9',
  blue: '#60a5fa',
  mono: 'Mono, ui-monospace, Menlo, monospace',
  sans: 'Sans, -apple-system, system-ui, sans-serif',
} as const;

export const hexA = (hex: string, a: number) => {
  const h = hex.replace('#', '');
  return `rgba(${parseInt(h.slice(0, 2), 16)}, ${parseInt(h.slice(2, 4), 16)}, ${parseInt(h.slice(4, 6), 16)}, ${a})`;
};

export const FORMAT = {fps: 30, width: 1920, height: 1080} as const;
export const sec = (s: number) => Math.round(s * FORMAT.fps);
