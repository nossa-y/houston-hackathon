// The acts. All mission data is REAL - from tonight's receipts (evidence/receipts/).
import './fonts';
import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {BRAND, hexA, sec} from './brand';
import {caret, fade, inOut, riseIn, typed} from './anim';
import {AppFrame, Card, ClaimsTable, FeedLine, Mono, ReceiptRow, Wordmark} from './ui';

const Center: React.FC<{children: React.ReactNode}> = ({children}) => (
  <AbsoluteFill style={{backgroundColor: BRAND.bg, alignItems: 'center', justifyContent: 'center'}}>
    {children}
  </AbsoluteFill>
);

const Caption: React.FC<{text: string; inAt: number; outAt: number}> = ({text, inAt, outAt}) => {
  const frame = useCurrentFrame();
  const o = inOut(frame, inAt, outAt);
  return (
    <div style={{
      position: 'absolute', bottom: 44, left: 0, right: 0, textAlign: 'center', opacity: o,
      fontFamily: BRAND.sans, fontSize: 30, fontWeight: 600, color: BRAND.text,
      textShadow: '0 2px 24px rgba(0,0,0,0.9)',
    }}>
      {text}
    </div>
  );
};

// ---------- ACT 0 · HOOK ----------
export const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const l1 = 'Tonight, 44 teams taught agents to use a computer.';
  const l2 = 'Every one of them will claim: task complete.';
  const l3 = 'Claims are not proof.';
  const mark = riseIn(frame, fps, sec(6.4));
  return (
    <Center>
      <div style={{width: 1280}}>
        <Mono size={34} color={BRAND.dim}>{typed(l1, frame, sec(0.4), 46, fps)}</Mono>
        <div style={{height: 26}} />
        <Mono size={34} color={BRAND.text}>{typed(l2, frame, sec(2.2), 46, fps)}</Mono>
        <div style={{height: 26}} />
        <div style={{opacity: fade(frame, sec(4.6), 8)}}>
          <Mono size={46} color={BRAND.red}>{l3}{frame < sec(6.2) ? <span style={{opacity: caret(frame)}}>▎</span> : null}</Mono>
        </div>
        <div style={{marginTop: 70, opacity: mark.opacity, transform: `translateY(${mark.y}px)`}}>
          <Wordmark size={54} />
          <div style={{fontFamily: BRAND.sans, color: BRAND.dim, fontSize: 22, marginTop: 14}}>
            mission control for computer-use agents
          </div>
        </div>
      </div>
    </Center>
  );
};

// ---------- ACT 1 · PROBLEM ----------
export const Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const a = riseIn(frame, fps, sec(0.3));
  const b = riseIn(frame, fps, sec(1.4));
  const c = riseIn(frame, fps, sec(2.4));
  return (
    <Center>
      <div style={{width: 1300}}>
        <div style={{opacity: a.opacity, transform: `translateY(${a.y}px)`}}>
          <div style={{fontFamily: BRAND.sans, fontSize: 52, fontWeight: 750, color: BRAND.text, lineHeight: 1.25}}>
            The most documented failure of computer-use agents:
          </div>
          <div style={{fontFamily: BRAND.mono, fontSize: 52, fontWeight: 700, color: BRAND.red, marginTop: 12}}>
            they say "done" when they are not.
          </div>
        </div>
        <div style={{marginTop: 54, opacity: b.opacity, transform: `translateY(${b.y}px)`}}>
          <div style={{borderLeft: `3px solid ${BRAND.line}`, paddingLeft: 24, color: BRAND.dim, fontFamily: BRAND.sans, fontSize: 26, lineHeight: 1.6}}>
            "agents produce empty results while claiming tasks complete"<br />
            "misread 15 for 5 · falsely claimed items unavailable · increasingly confused"
          </div>
        </div>
        <div style={{marginTop: 44, opacity: c.opacity, transform: `translateY(${c.y}px)`}}>
          <div style={{fontFamily: BRAND.mono, fontSize: 30, color: BRAND.green}}>
            Everyone says "verify agent output." Nobody ships the verifier.
          </div>
        </div>
      </div>
      <Caption text="Houston is the verifier." inAt={sec(4.6)} outAt={sec(9.4)} />
    </Center>
  );
};

// ---------- shared mission data (REAL, receipt d5914f0d8c93 + e32600d5a0ef) ----------
const TASK = 'Find every FIVE-star book in the Poetry category on books.toscrape.com and their total price.';
const CLAIM_1 = `6 books rated exactly five stars:

Quarter Life Poetry          £50.89
Out of Print: City Lights    £53.64
Les Fleurs du Mal            £29.04
Leave This Song Behind       £51.17
Collected Poems of Yeats     £15.42
Booked                       £17.49

Combined total: £217.65`;
const DIVERGENCE = 'The executor reported 6 five-star books totaling £217.65, but I observed 7 - it missed "Poems That Make Grown Women Cry" (£14.19).';
const DIAGNOSIS = 'Scroll through all 19 books in the Poetry category and count every book with 5 gold stars; sum all their prices.';
const CLAIM_2 = `7 books rated five stars (corrected):
the previous six, plus
Poems That Make Grown Women Cry   £14.19

Combined total: £231.84`;

// The three receipts that already existed when this mission ran (real data).
const PRIOR_RECEIPTS = (
  <>
    <ReceiptRow id="666aaaa507da" status="VERIFIED" task="Count Mystery books under £20 - every page." attempts={1} secs={129.2} hash="d6521265dc28331d" />
    <ReceiptRow id="13375571f60d" status="VERIFIED" task="Three most expensive Travel books + total." attempts={1} secs={91.4} hash="7312a649e60fa958" />
    <ReceiptRow id="fb135fc50a39" status="VERIFIED" task="Eiffel Tower height and completion year." attempts={1} secs={56.3} hash="ac4bc074a06bd761" />
  </>
);

// ---------- ACT 2 · LAUNCH + ATTEMPT ----------
export const ActLaunch: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = typed(TASK, frame, sec(0.5), 60, fps);
  const launched = frame > sec(2.6);
  const showClaim = frame > sec(8.2);
  return (
    <Center>
      <AppFrame
        receipts={10}
        task={t}
        taskCaret={!launched}
        active={launched ? 'attempt' : undefined}
        sidebar={PRIOR_RECEIPTS}
      >
        {launched && <FeedLine say text="Mission received. Executor launching." />}
        {frame > sec(3.6) && <FeedLine text="executor session 70d0aa02... " link />}
        {frame > sec(4.4) && <FeedLine say text="Agent is live. Houston is watching every step." />}
        {frame > sec(5.4) && <FeedLine text="working... step 4" />}
        {frame > sec(6.4) && <FeedLine text="working... step 7" />}
        {frame > sec(7.4) && <FeedLine say text="The agent claims the task is done. Houston never trusts a claim." />}
        {showClaim && (
          <Card kind="claim" title="AGENT CLAIMS DONE - ATTEMPT 1">
            <Mono size={14}>{CLAIM_1}</Mono>
          </Card>
        )}
      </AppFrame>
      <Caption text="Speak or type a mission. An H Company agent runs it on the real web." inAt={sec(1)} outAt={sec(6.5)} />
      <Caption text='The agent says: done.' inAt={sec(8.6)} outAt={sec(13.6)} />
    </Center>
  );
};

// ---------- ACT 3 · AUDIT REJECTS ----------
export const ActAudit: React.FC = () => {
  const frame = useCurrentFrame();
  const showVerdict = frame > sec(3.4);
  return (
    <Center>
      <AppFrame receipts={10} task={TASK} active="audit" done={['attempt']} sidebar={PRIOR_RECEIPTS}>
        <FeedLine say text="Verifying independently against the live site." />
        {frame > sec(1.2) && <FeedLine text="verifier session 2023fcf1... " link />}
        {frame > sec(2.2) && <FeedLine text="verifier re-deriving the answer with its own navigation" />}
        {showVerdict && (
          <Card kind="rejected" title="AUDIT: REJECTED · CONFIDENCE 100%">
            <Mono size={14} color={BRAND.text}>{DIVERGENCE}</Mono>
            <ClaimsTable rows={[
              {ok: true, claim: 'Six titles listed with prices', observed: 'titles and prices match the category page'},
              {ok: false, claim: 'Exactly 6 five-star books · total £217.65', observed: 'I count 7 five-star books · total £231.84'},
            ]} />
          </Card>
        )}
      </AppFrame>
      <Caption text="A second, independent agent re-checks reality. It disagrees." inAt={sec(0.6)} outAt={sec(5.4)} />
      <Caption text="No human in the loop. The claim simply does not survive." inAt={sec(6)} outAt={sec(10.4)} />
    </Center>
  );
};

// ---------- ACT 4 · HEAL ----------
export const ActHeal: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const d = typed(DIAGNOSIS, frame, sec(1.2), 80, fps);
  return (
    <Center>
      <AppFrame receipts={10} task={TASK} active="heal" done={['attempt', 'audit']} sidebar={PRIOR_RECEIPTS}>
        <FeedLine say text="Injecting the diagnosis into the live session. The agent gets a second chance." />
        <Card kind="heal" title="HEALING - RE-BRIEFING THE LIVE SESSION">
          <Mono size={14}>{d}</Mono>
        </Card>
        {frame > sec(4.6) && (
          <Card kind="claim" title="AGENT CLAIMS DONE - ATTEMPT 2 (HEALED)">
            <Mono size={14}>{CLAIM_2}</Mono>
          </Card>
        )}
        {frame > sec(7.2) && (
          <Card kind="confirmed" title="AUDIT: CONFIRMED · CONFIDENCE 100%">
            <Mono size={14} color={BRAND.dim}>the corrected claim matches what the verifier observed</Mono>
          </Card>
        )}
      </AppFrame>
      <Caption text="No restart. The SAME session is steered mid-run with the fix." inAt={sec(1)} outAt={sec(6)} />
      <Caption text="Attempt 2 verifies. Case closed?" inAt={sec(7.6)} outAt={sec(10.2)} />
    </Center>
  );
};

// ---------- ACT 5 · ARBITER (the 3:04 AM story) ----------
export const ActArbiter: React.FC = () => {
  const frame = useCurrentFrame();
  const showRuling = frame > sec(6.4);
  return (
    <Center>
      <AppFrame receipts={10} task={TASK} active="arbiter" done={['attempt', 'audit', 'heal']} sidebar={PRIOR_RECEIPTS}>
        <FeedLine say text="The two answers disagree. Escalating to the arbiter for close inspection." />
        {frame > sec(1.6) && <FeedLine text="arbiter session 751ac11d... " link />}
        {frame > sec(2.6) && <FeedLine text='opening "Poems That Make Grown Women Cry" on its own page' />}
        {frame > sec(4.2) && (
          <Card kind="arb" title="CLOSE INSPECTION">
            <Mono size={15}>
              {'Poems That Make Grown Women Cry\nrating displayed on its own page:  '}
              <span style={{color: BRAND.amber}}>★★★★</span>
              <span style={{color: BRAND.dim}}>☆  FOUR stars - not five</span>
            </Mono>
          </Card>
        )}
        {showRuling && (
          <Card kind="arb" title="ARBITER RULING: ATTEMPT ORIGINAL">
            <Mono size={14}>
              The verifier misread a four-star badge in a dense list. The agent was right
              the first time. Original answer restored: 6 books · £217.65.
            </Mono>
          </Card>
        )}
      </AppFrame>
      <Caption text="This really happened at 2:13 AM tonight. Our verifier gaslit a CORRECT agent." inAt={sec(1.2)} outAt={sec(5.8)} />
      <Caption text="So Houston doubts its own verifier: quorum under dispute." inAt={sec(6.6)} outAt={sec(12.4)} />
    </Center>
  );
};

// ---------- ACT 6 · PROOF ----------
export const ActProof: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Center>
      <AppFrame
        receipts={11}
        task={TASK}
        active="proof"
        done={['attempt', 'audit', 'heal', 'arbiter']}
        sidebar={
          <>
            <ReceiptRow id="d5914f0d8c93" status="VERIFIED-BY-ARBITER" statusKind="cyan" task={TASK} attempts={2} secs={168.8} hash="37c009c14dcb7cff" />
            {frame > sec(2.2) && <ReceiptRow id="666aaaa507da" status="VERIFIED" task="Count Mystery books under £20 - every page." attempts={1} secs={129.2} hash="d6521265dc28331d" />}
            {frame > sec(3.0) && <ReceiptRow id="dea91ef5c7c5" status="VERIFIED" task="Most expensive book in Classics." attempts={1} secs={84.3} hash="9f01c822e41ab6d0" />}
            {frame > sec(3.8) && <ReceiptRow id="fb135fc50a39" status="VERIFIED" task="Eiffel Tower height and completion year." attempts={1} secs={56.3} hash="ac4bc074a06bd761" />}
          </>
        }
      >
        <Card kind="confirmed" title="RECEIPT SEALED · VERIFIED-BY-ARBITER (ORIGINAL ANSWER RESTORED)" style={{marginTop: 18}}>
          <Mono size={15}>{'6 five-star books · combined total £217.65'}</Mono>
          <div style={{display: 'flex', gap: 12, marginTop: 12, fontFamily: BRAND.mono, fontSize: 12}}>
            <span style={{color: BRAND.blue, border: `1px solid ${BRAND.line}`, padding: '6px 12px', borderRadius: 8}}>executor replay ↗</span>
            <span style={{color: BRAND.blue, border: `1px solid ${BRAND.line}`, padding: '6px 12px', borderRadius: 8}}>audit 1 ↗</span>
            <span style={{color: BRAND.blue, border: `1px solid ${BRAND.line}`, padding: '6px 12px', borderRadius: 8}}>audit 2 ↗</span>
            <span style={{color: BRAND.blue, border: `1px solid ${BRAND.line}`, padding: '6px 12px', borderRadius: 8}}>arbiter ↗</span>
          </div>
          <div style={{marginTop: 12, fontFamily: BRAND.mono, fontSize: 12, color: BRAND.dim}}>
            #37c009c14dcb7cff ← #d6521265dc28331d <span style={{color: BRAND.green}}>· chain INTACT</span>
          </div>
        </Card>
      </AppFrame>
      <Caption text="Every mission ends in a hash-chained receipt with step-level replays." inAt={sec(0.8)} outAt={sec(5.6)} />
      <Caption text="Proof, not promises." inAt={sec(6.2)} outAt={sec(9.4)} />
    </Center>
  );
};

// ---------- ACT 7 · STACK ----------
const StackPanel: React.FC<{title: string; color: string; lines: string[]; at: number}> = ({title, color, lines, at}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const r = riseIn(frame, fps, at);
  return (
    <div style={{
      flex: 1, background: BRAND.panel, border: `1px solid ${BRAND.line}`, borderTop: `3px solid ${color}`,
      borderRadius: 14, padding: 28, opacity: r.opacity, transform: `translateY(${r.y}px)`,
    }}>
      <div style={{fontFamily: BRAND.mono, fontWeight: 800, fontSize: 22, letterSpacing: '0.12em', color}}>{title}</div>
      {lines.map((l, i) => (
        <div key={i} style={{fontFamily: BRAND.sans, fontSize: 18, color: i === lines.length - 1 ? BRAND.dim : BRAND.text, marginTop: 16, lineHeight: 1.45}}>
          {l}
        </div>
      ))}
    </div>
  );
};

export const ActStack: React.FC = () => (
  <Center>
    <div style={{width: 1640}}>
      <div style={{fontFamily: BRAND.sans, fontSize: 40, fontWeight: 750, color: BRAND.text, marginBottom: 34, textAlign: 'center'}}>
        Three agents per mission. Three layers of the stack.
      </div>
      <div style={{display: 'flex', gap: 22}}>
        <StackPanel title="H COMPANY" color={BRAND.blue} at={sec(0.6)} lines={[
          'Executor, verifier and arbiter are separate live sessions on the Agent Platform.',
          'Healing = send_message steering into the SAME session. Verdicts = typed answer schemas.',
          'Every step scrubbable in agent-view replays.',
        ]} />
        <StackPanel title="GRADIUM" color={BRAND.green} at={sec(1.4)} lines={[
          'Missions are spoken in: streaming STT with word-level partials.',
          'Houston talks back: every phase narrated in 48 kHz streaming TTS.',
          'Voice loop self-tested end to end: TTS speaks, STT hears, 92% overlap.',
        ]} />
        <StackPanel title="NVIDIA" color={BRAND.cyan} at={sec(2.2)} lines={[
          'Evidence screenshots audited ON-DEVICE: Holo-3.1-35B-A3B GGUF via llama.cpp.',
          '~10 s per audit on Apple Silicon. Zero screenshot bytes leave the machine.',
          'Ships a NemoClaw sandbox config + the first computer-use community blueprint.',
        ]} />
      </div>
    </div>
    <Caption text="Deep in every sponsor stack - by necessity, not decoration." inAt={sec(4)} outAt={sec(10)} />
  </Center>
);

// ---------- ACT 8 · OUTRO ----------
export const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const n = Math.min(11, Math.floor(Math.max(0, frame - sec(0.6)) / 4));
  const mark = riseIn(frame, fps, sec(2.6));
  return (
    <Center>
      <div style={{textAlign: 'center'}}>
        <div style={{fontFamily: BRAND.mono, fontSize: 30, color: BRAND.dim}}>
          built in one night. battle-tested all night.
        </div>
        <div style={{fontFamily: BRAND.mono, fontSize: 44, color: BRAND.text, marginTop: 22}}>
          <span style={{color: BRAND.green, fontWeight: 800}}>{n}</span> real missions receipted tonight ·{' '}
          <span style={{color: BRAND.green}}>chain INTACT</span>
        </div>
        <div style={{marginTop: 80, opacity: mark.opacity, transform: `translateY(${mark.y}px)`}}>
          <Wordmark size={84} />
          <div style={{fontFamily: BRAND.sans, fontSize: 30, color: BRAND.text, marginTop: 26, fontWeight: 600}}>
            Never trust. Always verify.
          </div>
          <div style={{fontFamily: BRAND.mono, fontSize: 19, color: BRAND.dim, marginTop: 30}}>
            Team HOUSTON · The Computer Use Hackathon · built on H Company agents · July 2026
          </div>
        </div>
      </div>
    </Center>
  );
};
