# write-up.md — Design Rationale for the Daily Reflection Tree

## Why These Questions

The hardest part of this assignment wasn't the code — it was writing questions that a tired person at 7pm would actually stop and *feel*. Bad reflection questions are binary traps ("Were you productive today?") or obvious virtue signals ("Did you help someone today?"). Good ones are mirrors — they hold up something the person hadn't named yet.

### Axis I — Locus of Control

Rotter's original locus-of-control scale asked people to choose between paired statements — "What happens to me is my own doing" vs "Sometimes I feel I don't have enough control over the direction my life is taking." The genius of the instrument was that both options were *defensible*. Neither felt like a trap.

I tried to preserve that quality. When the opening question routes someone to `A1_Q2_LOW` (hard day), the follow-up question — *"When things got hard, what was your first instinct?"* — offers "Push through regardless" as an internal-locus option. This is intentional: someone can show agency through stubbornness, not just wisdom. The tree doesn't reward the "best" answer; it reflects the *real* one.

The third Axis I question — *"What did you do with that feeling of losing control?"* — is where Dweck enters. A growth mindset doesn't mean pretending difficult emotions aren't there; it means using them as information. The option "Acknowledged it, then focused on what I could still change" captures that: the acknowledgment matters as much as the pivot.

### Axis II — Contribution vs Entitlement

Campbell et al.'s entitlement scale measures a stable dispositional trait — but entitlement is most legible in its *behavioral* expressions: monitoring credit, withdrawing effort, feeling cheated by systems. I didn't ask "are you entitled?" (nobody says yes). Instead I asked about concrete moments: what prompted the giving, what happened when recognition didn't come, whether recognition would have changed behavior.

The third question — *"If no one noticed anything you did today, would you have shown up differently?"* — is the diagnostic one. It's impossible to answer self-servingly without pausing. The honest "yes, actually" options are written with dignity: "I need to feel seen to keep going" and "I'm exhausted by giving without return" are not shameful confessions — they're states that require acknowledgment before they can shift.

### Axis III — Radius of Concern

Maslow's 1969 paper *"The Farther Reaches of Human Nature"* introduced self-transcendence as a stage above self-actualization — the shift from "I want to be all I can be" to "I want to be of use to something larger than myself." The key word is *radius*: how wide is the circle of people whose experience you hold in awareness?

The axis opens with a concrete question about whose face comes to mind during the hardest moment. This was inspired by Batson's perspective-taking research — empathy as a *cognitive* act, not just a feeling. "The person we're ultimately trying to serve" is the widest option: it names the customer or end-user who is abstract but real.

The narrowing/widening follow-up questions (`A3_Q2_NARROW` vs `A3_Q2_WIDE`) are designed to avoid shame. Someone who answered narrowly isn't bad — they're honest. The follow-up asks *what triggers the widening*, which is more useful than accusation.

---

## How the Branching Works

### Two-level decision pattern

Each axis follows the same structure:
1. **Entry question** → routes to a `decision` node based on the raw answer
2. **Decision node (D1)** → `answer_in` condition checks which pole the opening question activated → two different follow-up question paths
3. **Follow-up question** → accumulates `signal` tallies
4. **Closing question** → accumulates final signal
5. **Decision node (D2)** → `signal_dominant` condition determines which reflection the user sees

This two-level architecture means the *opening mood* sets context, but the *closing question* has the most weight. Someone who opens "Frustrating" but then answers every follow-up with internal-locus choices will still get the internal reflection. The tree tracks behavior, not just mood.

### Signals and tallies

Each answer carries a `signal` tag (`axis1:internal`, `axis2:contribution`, etc.). The decision nodes that route to reflections use `signal_dominant` — they check which pole has accumulated more tallies across the axis. This means:
- A person can be "mostly internal" without being perfectly consistent
- Outlier answers don't derail the whole path
- The summary can make honest statements like "you leaned toward..."

### Trade-offs

**Fixed options vs nuance.** The hardest constraint was the no-free-text rule. I lost a lot of nuance — someone's actual day is always richer than four choices. My mitigation was writing option text that covers a wide behavioral range per pole, and making sure neither pole's options felt like the "loser" answer.

**Depth vs speed.** With three questions per axis and two per axis covered by branching, the session is 9–10 questions total. That's 7–10 minutes at a reflective pace. I could have gone deeper (5 questions per axis), but the assignment's brief is *end-of-day* — people won't do this if it takes 20 minutes.

**Tone.** Every reflection node was written 3+ times. The failure mode is moralizing: "You showed victim thinking today — try to be more proactive!" The target tone is a wise colleague who has seen a lot of days and doesn't need to teach you anything — just name what they notice.

---

## What Psychology Informed the Design

| Source | Where it shows up |
|--------|-------------------|
| Rotter (1954), Locus of Control | Axis I question design; internal/external framing |
| Dweck (2006), Mindset | "What did you do with that feeling?" — the pivot question |
| Campbell et al. (2004), Entitlement | Axis II; behavioral (not attitudinal) entitlement signals |
| Organ (1988), OCB | Axis II; discretionary effort and "giving without a receipt" |
| Maslow (1969), Self-transcendence | Axis III opening; the radius framing |
| Batson (2011), Perspective-taking | Axis III; "whose experience comes to mind" |

---

## What I'd Improve With More Time

1. **Longitudinal signal tracking.** Right now each session is stateless. Over 30 sessions, the tree could show trends: "Your external-locus signals peak on Tuesdays" or "Your contribution score dropped this quarter." This requires a simple DB write at session end — the tree data structure already supports it.

2. **Axis interconnection.** The spec notes that the axes are meant to *build* — agency unlocks contribution; contribution widens radius. My current bridge nodes gesture at this ("from how you handled things, to what you gave"), but the follow-up questions don't reference earlier axis answers deeply enough. Ideal next step: have Axis II's questions interpolate Axis I signals — e.g., "You said you found ways to adapt today (`{A1_Q2_HIGH.answer}`). Did that capacity extend to the people around you?"

3. **Branching on persona combinations.** Currently each axis branches independently. A richer tree would cross-route: someone who is *external* on Axis I *and* entitlement-oriented on Axis II would see a specific Axis III reflection about self-protection vs. contribution — not just the generic radius reflection.

4. **Calibration question at start.** Adding an optional "how much time do you have?" node that lets the user select a 3-question sprint vs the full 10-question session would dramatically improve daily completion rates.