# Daily Reflection Tree

A deterministic end-of-day reflection tool. No LLM at runtime — pure tree traversal.

## Running the App

```bash
pip install streamlit
streamlit run app.py
```

The app opens at `http://localhost:8501` by default.

## File Structure

```
/
├── app.py                  ← Streamlit agent (tree engine)
├── reflection_tree.json    ← The tree data (28 nodes)
├── write-up.md             ← Design rationale
├── requirements.txt
└── .streamlit/
    └── config.toml         ← Dark theme settings
```

## Tree Stats

| Metric | Count |
|--------|-------|
| Total nodes | 28 |
| Question nodes | 12 |
| Decision nodes | 5 |
| Reflection nodes | 6 |
| Bridge nodes | 2 |
| Summary node | 1 |
| Axes covered | 3 (Locus · Contribution · Radius) |

## How the Tree Works

1. The engine loads `reflection_tree.json` at startup
2. Session state tracks: current node, all answers, per-axis signal tallies, path history
3. **Question nodes** → render options → user picks one → tally signal → navigate to next
4. **Decision nodes** → invisible to user → evaluate `answer_in` or `signal_dominant` condition → jump to result
5. **Reflection/Bridge/Summary** → display text (interpolated with earlier answers) → continue
6. Same answers always produce the same path. No randomness. No AI calls.

## Two Personas (Sample Paths)

**Victor/Contributor/Altrocentric:**
START → A1_OPEN(Productive) → A1_Q2_HIGH → A1_Q3 → A1_R_INTERNAL → BRIDGE_1_2 →
A2_OPEN(helped someone) → A2_Q2_CONTRIB → A2_Q3 → A2_R_CONTRIBUTION → BRIDGE_2_3 →
A3_OPEN(colleague had it harder) → A3_Q2_WIDE → A3_Q3 → A3_R_ALTROCENTRIC → SUMMARY → END

**Victim/Entitled/Self-Centric:**
START → A1_OPEN(Frustrating) → A1_Q2_LOW → A1_Q3 → A1_R_EXTERNAL → BRIDGE_1_2 →
A2_OPEN(felt let down) → A2_Q2_ENTITLE → A2_Q3 → A2_R_ENTITLEMENT → BRIDGE_2_3 →
A3_OPEN(just mine) → A3_Q2_NARROW → A3_Q3 → A3_R_SELFCENTRIC → SUMMARY → END
