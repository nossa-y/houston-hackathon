// Composition registry. `Launch` is the 16:9 master; `LaunchVertical` is the 9:16 cut;
// `TitleCard` is the outro on its own (handy for iterating the brand card).
import {Composition} from 'remotion';
import {FORMAT} from './brand';
import {Launch, LaunchVertical, LAUNCH_DURATION} from './Launch';
import {TitleCard} from './TitleCard';

export const RemotionRoot = () => (
  <>
    <Composition id="Launch" component={Launch} durationInFrames={LAUNCH_DURATION} {...FORMAT} />
    <Composition id="LaunchVertical" component={LaunchVertical} durationInFrames={LAUNCH_DURATION} fps={FORMAT.fps} width={1080} height={1920} />
    <Composition id="TitleCard" component={TitleCard} durationInFrames={FORMAT.fps * 6} {...FORMAT} />
  </>
);
