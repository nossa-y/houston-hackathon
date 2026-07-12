// Pixel-faithful recreation of Houston's mission-control UI (houston/static/index.html).
import React from 'react';
import {BRAND, hexA} from './brand';

export const Wordmark: React.FC<{size?: number}> = ({size = 26}) => (
  <div style={{fontFamily: BRAND.mono, fontWeight: 800, fontSize: size, letterSpacing: '0.35em', color: BRAND.text}}>
    H<span style={{color: BRAND.green}}>OU</span>STON
  </div>
);

export const AppHeader: React.FC<{receipts?: number}> = ({receipts = 11}) => (
  <div style={{display: 'flex', alignItems: 'baseline', gap: 16, borderBottom: `1px solid ${BRAND.line}`, paddingBottom: 14}}>
    <Wordmark />
    <div style={{color: BRAND.dim, fontSize: 13, fontFamily: BRAND.sans}}>
      mission control for computer-use agents - never trust, always verify
    </div>
    <div style={{marginLeft: 'auto', fontFamily: BRAND.mono, fontSize: 12, color: BRAND.dim}}>
      chain <span style={{color: BRAND.green}}>INTACT</span> · {receipts} receipts
    </div>
  </div>
);

const phaseColor: Record<string, string> = {
  attempt: BRAND.blue, audit: BRAND.blue, heal: BRAND.amber, arbiter: BRAND.cyan, proof: BRAND.blue,
};

export const PhasePills: React.FC<{active?: string; done?: string[]}> = ({active, done = []}) => (
  <div style={{display: 'flex', gap: 8, margin: '18px 0 6px'}}>
    {['attempt', 'audit', 'heal', 'arbiter', 'proof'].map((p) => {
      const isActive = active === p;
      const isDone = done.includes(p);
      return (
        <div key={p} style={{
          fontFamily: BRAND.mono, fontWeight: 600, fontSize: 11, letterSpacing: '0.14em',
          color: isActive ? '#04110b' : isDone ? BRAND.green : BRAND.dim,
          background: isActive ? phaseColor[p] : 'transparent',
          border: `1px solid ${isActive ? phaseColor[p] : isDone ? BRAND.green : BRAND.line}`,
          borderRadius: 99, padding: '8px 14px',
        }}>
          {p.toUpperCase()}
        </div>
      );
    })}
  </div>
);

export const TaskRow: React.FC<{value: string; caret?: boolean; micActive?: boolean}> = ({value, caret, micActive}) => (
  <div style={{display: 'flex', gap: 10}}>
    <div style={{
      flex: 1, background: BRAND.panel2, border: `1px solid ${value ? BRAND.blue : BRAND.line}`,
      borderRadius: 9, color: value ? BRAND.text : BRAND.dim, padding: '12px 14px', fontSize: 15,
      fontFamily: BRAND.sans, whiteSpace: 'nowrap', overflow: 'hidden',
    }}>
      {value || 'Give the agent a mission - type it, or press the mic and speak it'}
      {caret ? <span style={{color: BRAND.green}}>▎</span> : null}
    </div>
    <div style={{
      border: `1px solid ${micActive ? BRAND.red : BRAND.line}`, borderRadius: 9,
      color: micActive ? BRAND.red : BRAND.dim, padding: '12px 16px', fontSize: 14,
    }}>
      {micActive ? '■' : '🎙'}
    </div>
    <div style={{
      background: BRAND.green, borderRadius: 9, color: '#04110b', fontWeight: 700,
      padding: '12px 20px', fontSize: 14, fontFamily: BRAND.sans, letterSpacing: '0.02em',
    }}>
      LAUNCH
    </div>
  </div>
);

export const FeedLine: React.FC<{text: string; say?: boolean; link?: boolean}> = ({text, say, link}) => (
  <div style={{
    fontFamily: BRAND.mono, fontSize: 13, color: say ? BRAND.text : BRAND.dim,
    padding: '7px 12px', background: BRAND.panel2, borderRadius: 8,
    borderLeft: `2px solid ${say ? BRAND.green : BRAND.line}`, marginBottom: 8,
    whiteSpace: 'nowrap', overflow: 'hidden',
  }}>
    {text}{link ? <span style={{color: BRAND.blue}}> watch live ↗</span> : null}
  </div>
);

export const Card: React.FC<{
  kind: 'claim' | 'rejected' | 'confirmed' | 'heal' | 'arb';
  title: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}> = ({kind, title, children, style}) => {
  const edge = {claim: BRAND.blue, rejected: BRAND.red, confirmed: BRAND.green, heal: BRAND.amber, arb: BRAND.cyan}[kind];
  const titleColor = kind === 'claim' ? BRAND.dim : edge;
  return (
    <div style={{
      borderRadius: 12, padding: 16, border: `1px solid ${BRAND.line}`, borderLeft: `3px solid ${edge}`,
      background: BRAND.panel2, marginTop: 14, ...style,
    }}>
      <div style={{fontFamily: BRAND.mono, fontWeight: 700, fontSize: 12, letterSpacing: '0.18em', color: titleColor, marginBottom: 8}}>
        {title}
      </div>
      {children}
    </div>
  );
};

export const Mono: React.FC<{children: React.ReactNode; size?: number; color?: string}> = ({children, size = 13, color = BRAND.text}) => (
  <div style={{fontFamily: BRAND.mono, fontSize: size, lineHeight: 1.55, color, whiteSpace: 'pre-wrap'}}>{children}</div>
);

export const ClaimsTable: React.FC<{rows: Array<{ok: boolean; claim: string; observed: string}>}> = ({rows}) => (
  <table style={{width: '100%', borderCollapse: 'collapse', marginTop: 8, fontFamily: BRAND.mono, fontSize: 12.5}}>
    <tbody>
      {rows.map((r, i) => (
        <tr key={i}>
          <td style={{padding: '6px 8px', borderTop: `1px solid ${BRAND.line}`, color: r.ok ? BRAND.green : BRAND.red, width: 30}}>
            {r.ok ? 'OK' : '✗'}
          </td>
          <td style={{padding: '6px 8px', borderTop: `1px solid ${BRAND.line}`, color: BRAND.text}}>{r.claim}</td>
          <td style={{padding: '6px 8px', borderTop: `1px solid ${BRAND.line}`, color: BRAND.dim}}>{r.observed}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

export const ReceiptRow: React.FC<{
  id: string; status: string; task: string; attempts: number; secs: number; hash: string; statusKind?: 'green' | 'cyan' | 'red';
}> = ({id, status, task, attempts, secs, hash, statusKind = 'green'}) => {
  const c = {green: BRAND.green, cyan: BRAND.cyan, red: BRAND.red}[statusKind];
  return (
    <div style={{border: `1px solid ${BRAND.line}`, borderRadius: 10, padding: 12, marginBottom: 10, background: BRAND.panel2}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontFamily: BRAND.mono, fontSize: 12, color: BRAND.text}}>
        <span>{id}</span>
        <span style={{fontWeight: 700, fontSize: 10.5, letterSpacing: '0.1em', padding: '3px 9px', borderRadius: 99, background: hexA(c, 0.14), color: c}}>
          {status}
        </span>
      </div>
      <div style={{color: BRAND.dim, fontSize: 12.5, marginTop: 6, fontFamily: BRAND.sans, overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis'}}>
        {task}
      </div>
      <div style={{marginTop: 8, fontFamily: BRAND.mono, fontSize: 10.5, color: BRAND.dim, display: 'flex', gap: 9, whiteSpace: 'nowrap', overflow: 'hidden'}}>
        <span>{attempts} attempt{attempts === 1 ? '' : 's'}</span>
        <span>{secs}s</span>
        <span style={{color: BRAND.cyan}}>#{hash.slice(0, 10)}</span>
        <span style={{color: BRAND.blue}}>replay ↗</span>
      </div>
    </div>
  );
};

// The full app frame: header + main panel + receipts sidebar.
export const AppFrame: React.FC<{
  receipts?: number;
  active?: string;
  done?: string[];
  task?: string;
  taskCaret?: boolean;
  micActive?: boolean;
  children?: React.ReactNode;
  sidebar?: React.ReactNode;
}> = ({receipts, active, done, task = '', taskCaret, micActive, children, sidebar}) => (
  <div style={{
    width: 1590, background: BRAND.bg, border: `1px solid ${BRAND.line}`, borderRadius: 18,
    padding: '22px 28px', boxShadow: '0 40px 120px rgba(0,0,0,0.55)',
  }}>
    <AppHeader receipts={receipts} />
    <div style={{display: 'grid', gridTemplateColumns: '1fr 360px', gap: 20, marginTop: 20}}>
      <div style={{background: BRAND.panel, border: `1px solid ${BRAND.line}`, borderRadius: 12, padding: 18, minHeight: 560}}>
        <TaskRow value={task} caret={taskCaret} micActive={micActive} />
        <PhasePills active={active} done={done} />
        {children}
      </div>
      <div style={{background: BRAND.panel, border: `1px solid ${BRAND.line}`, borderRadius: 12, padding: 18, minHeight: 560}}>
        <div style={{fontFamily: BRAND.mono, fontWeight: 700, fontSize: 13, letterSpacing: '0.2em', color: BRAND.dim, marginBottom: 12}}>
          RECEIPTS
        </div>
        {sidebar}
      </div>
    </div>
  </div>
);
