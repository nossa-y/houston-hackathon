// Assembly: 9 acts joined by short cross-fades. ~102s master @30fps.
import {AbsoluteFill} from 'remotion';
import {linearTiming, TransitionSeries} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {BRAND, sec} from './brand';
import {ActArbiter, ActAudit, ActHeal, ActLaunch, ActProof, ActStack, Hook, Outro, Problem} from './scenes';

const T = 10;
const DUR = [sec(8.5), sec(10.5), sec(14.5), sec(11), sec(10.5), sec(13), sec(10), sec(11), sec(10.5)];
export const LAUNCH_DURATION = DUR.reduce((a, b) => a + b, 0) - (DUR.length - 1) * T;
const timing = linearTiming({durationInFrames: T});

export const Launch = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence durationInFrames={DUR[0]}><Hook /></TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={timing} />
    <TransitionSeries.Sequence durationInFrames={DUR[1]}><Problem /></TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={timing} />
    <TransitionSeries.Sequence durationInFrames={DUR[2]}><ActLaunch /></TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={timing} />
    <TransitionSeries.Sequence durationInFrames={DUR[3]}><ActAudit /></TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={timing} />
    <TransitionSeries.Sequence durationInFrames={DUR[4]}><ActHeal /></TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={timing} />
    <TransitionSeries.Sequence durationInFrames={DUR[5]}><ActArbiter /></TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={timing} />
    <TransitionSeries.Sequence durationInFrames={DUR[6]}><ActProof /></TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={timing} />
    <TransitionSeries.Sequence durationInFrames={DUR[7]}><ActStack /></TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={timing} />
    <TransitionSeries.Sequence durationInFrames={DUR[8]}><Outro /></TransitionSeries.Sequence>
  </TransitionSeries>
);

export const LaunchVertical = () => (
  <AbsoluteFill style={{backgroundColor: BRAND.bg, overflow: 'hidden', alignItems: 'center', justifyContent: 'center'}}>
    <div style={{width: 1920, height: 1080, position: 'relative', flexShrink: 0, transform: 'scale(1.18)'}}>
      <Launch />
    </div>
  </AbsoluteFill>
);
