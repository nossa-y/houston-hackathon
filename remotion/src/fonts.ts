import {continueRender, delayRender, staticFile} from 'remotion';

const handle = delayRender('Loading brand fonts');

const mono = new FontFace('Mono', `url(${staticFile('Mono.ttf')})`, {weight: '100 800'});
const sans = new FontFace('Sans', `url(${staticFile('Sans.ttf')})`, {weight: '100 900'});

Promise.all([mono.load(), sans.load()])
  .then((faces) => {
    faces.forEach((f) => (document.fonts as unknown as {add(f: FontFace): void}).add(f));
    continueRender(handle);
  })
  .catch(() => continueRender(handle));
