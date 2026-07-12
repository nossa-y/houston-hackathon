// Branded outro card (also used standalone as a poster comp).
import './fonts';
import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {BRAND, sec} from './brand';
import {riseIn} from './anim';
import {Wordmark} from './ui';

export const TitleCard: React.FC<{holdEnd?: boolean}> = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const r = riseIn(frame, fps, sec(0.3));
  return (
    <AbsoluteFill style={{backgroundColor: BRAND.bg, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{textAlign: 'center', opacity: r.opacity, transform: `translateY(${r.y}px)`}}>
        <Wordmark size={84} />
        <div style={{fontFamily: BRAND.sans, fontSize: 30, color: BRAND.text, marginTop: 26, fontWeight: 600}}>
          Never trust. Always verify.
        </div>
      </div>
    </AbsoluteFill>
  );
};
