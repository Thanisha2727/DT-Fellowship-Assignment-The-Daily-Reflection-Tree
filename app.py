"""
Daily Reflection Tree — Deterministic End-of-Day Reflection Agent
No LLM at runtime. Pure tree traversal.
"""
import json
import streamlit as st
from pathlib import Path

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Daily Reflection",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Load tree ────────────────────────────────────────────────────────────────
@st.cache_data
def load_tree():
    p = Path(__file__).parent / "reflection_tree.json"
    return json.loads(p.read_text())

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Layout ── */
.stApp { background: #080d1a !important; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1200px; }
div[data-testid="column"] { padding: 0 12px; }

/* ── Typography ── */
h1, h2, h3, p, li { color: #d4d8f0 !important; }

/* ── Buttons (option choices) ── */
.stButton > button {
    background: rgba(10, 25, 55, 0.7) !important;
    color: #9bb3e8 !important;
    border: 1px solid rgba(83, 130, 251, 0.25) !important;
    border-radius: 10px !important;
    padding: 13px 20px !important;
    font-size: 14px !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
    line-height: 1.4 !important;
    margin-bottom: 4px !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: rgba(83, 130, 251, 0.18) !important;
    border-color: rgba(83, 130, 251, 0.7) !important;
    color: #c5d5ff !important;
    transform: translateX(4px) !important;
}
/* Primary Continue / Begin buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #1a3a70 0%, #0d2250 100%) !important;
    border: 1px solid rgba(83, 130, 251, 0.6) !important;
    color: #7eb8ff !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div { background: linear-gradient(90deg, #3567e8, #53d8fb) !important; }

/* ── Divider ── */
hr { border-color: #1a2540 !important; }

/* ── Axis pill ── */
.axis-pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
}

/* ── Graphviz chart ── */
.stGraphVizChart { background: transparent !important; }
svg { background: transparent !important; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Session state ────────────────────────────────────────────────────────────
def init():
    if "initialized" not in st.session_state:
        st.session_state.update({
            "initialized": True,
            "current":     "START",
            "answers":     {},
            "signals":     {
                "axis1": {"internal": 0,     "external": 0},
                "axis2": {"contribution": 0, "entitlement": 0},
                "axis3": {"altrocentric": 0, "selfcentric": 0},
            },
            "path": ["START"],
        })

# ─── Tree engine helpers ──────────────────────────────────────────────────────
def go(node_id: str):
    st.session_state.current = node_id
    if node_id not in st.session_state.path:
        st.session_state.path.append(node_id)

def tally(signal: str):
    if signal:
        axis, pole = signal.split(":")
        st.session_state.signals[axis][pole] += 1

def dominant(axis: str) -> str:
    s = st.session_state.signals[axis]
    if sum(s.values()) == 0:
        return list(s)[0]
    return max(s, key=s.get)

def decide(node: dict) -> str | None:
    for c in node.get("conditions", []):
        if c.get("type") == "answer_in":
            ans = st.session_state.answers.get(c["node"], {}).get("text", "")
            if ans in c["values"]:
                return c["goTo"]
        elif c.get("type") == "signal_dominant":
            if dominant(c["axis"]) == c["dominant"]:
                return c["goTo"]
        elif "else" in c:
            return c["else"]
    return None

SUMMARY_TEXT = {
    "axis1": {
        "internal": "you stayed in contact with your own agency",
        "external": "your attention was pulled outward to circumstances",
    },
    "axis2": {
        "contribution": "you gave more than you kept score of",
        "entitlement": "the ledger was weighing on you",
    },
    "axis3": {
        "altrocentric": "others were inside your frame of concern",
        "selfcentric": "your own experience was the primary lens",
    },
}

def interpolate(text: str) -> str:
    for nid, ans in st.session_state.answers.items():
        text = text.replace("{" + nid + ".answer}", ans.get("text", ""))
    for ax in ["axis1", "axis2", "axis3"]:
        dom = dominant(ax)
        text = text.replace("{" + ax + "_dominant}", dom)
        text = text.replace("{" + ax + "_summary}", SUMMARY_TEXT[ax][dom])
    return text

# ─── Progress ─────────────────────────────────────────────────────────────────
MILESTONES = ["START", "A1_Q3", "BRIDGE_1_2", "A2_Q3", "BRIDGE_2_3", "A3_Q3", "SUMMARY"]

def get_progress() -> float:
    path = st.session_state.path
    reached = 0
    for i, m in enumerate(MILESTONES):
        if m in path:
            reached = i
    return reached / (len(MILESTONES) - 1)

def get_axis_label() -> str:
    c = st.session_state.current
    if c in ("START",) or c.startswith("A1"):
        return "Axis I  ·  Locus of Control"
    elif c == "BRIDGE_1_2" or c.startswith("A2"):
        return "Axis II  ·  Contribution vs Entitlement"
    elif c == "BRIDGE_2_3" or c.startswith("A3"):
        return "Axis III  ·  Radius of Concern"
    return "Summary"

# ─── Graphviz tree visualization ─────────────────────────────────────────────
TYPE_SHAPE = {
    "start":      "ellipse",
    "question":   "box",
    "decision":   "diamond",
    "reflection": "note",
    "bridge":     "parallelogram",
    "summary":    "octagon",
    "end":        "ellipse",
}
TYPE_COLOR = {
    "start":      ("#0d2e1a", "#52b788"),
    "question":   ("#0a1e3a", "#7eb8ff"),
    "decision":   ("#160e2e", "#ce93d8"),
    "reflection": ("#0d200d", "#a5d6a7"),
    "bridge":     ("#061a24", "#80deea"),
    "summary":    ("#260a0a", "#ef9a9a"),
    "end":        ("#111111", "#666666"),
}

def build_dot(nodes: dict, path: list, current: str) -> str:
    path_set = set(path)
    lines = [
        "digraph {",
        '  rankdir=TB;',
        '  bgcolor="transparent";',
        '  node [fontname="Arial" fontsize=9 style=filled margin="0.14,0.07"];',
        '  edge [fontname="Arial" fontsize=7];',
        "",
    ]

    # Clusters by axis
    clusters = {
        "cluster_a1": ([n for n in nodes if n.startswith("A1") or n == "START"],
                       "Axis I: Locus", "#0a1830", "#1a2a50"),
        "cluster_b1": (["BRIDGE_1_2"],     "",          "#060e18", "#0d1830"),
        "cluster_a2": ([n for n in nodes if n.startswith("A2")],
                       "Axis II: Contribution", "#0a1820", "#0d2a1a"),
        "cluster_b2": (["BRIDGE_2_3"],     "",          "#060e18", "#0d1830"),
        "cluster_a3": ([n for n in nodes if n.startswith("A3")],
                       "Axis III: Radius", "#0f0a20", "#1a0d30"),
        "cluster_end": (["SUMMARY", "END"], "Summary",  "#180808", "#300a0a"),
    }

    def node_dot(nid, node):
        ntype = node.get("type", "question")
        shape = TYPE_SHAPE.get(ntype, "box")
        bg, fg = TYPE_COLOR.get(ntype, ("#111", "#ccc"))
        lbl = node.get("label", nid).replace('"', '\\"')
        if nid == current:
            return (f'  "{nid}" [label="{lbl}" shape={shape} fillcolor="{bg}" '
                    f'fontcolor="{fg}" color="#FFD700" penwidth=2.5];')
        elif nid in path_set:
            return (f'  "{nid}" [label="{lbl}" shape={shape} fillcolor="{bg}" '
                    f'fontcolor="{fg}" color="{fg}" penwidth=1.5];')
        else:
            return (f'  "{nid}" [label="{lbl}" shape={shape} fillcolor="#0a0a0a" '
                    f'fontcolor="#252525" color="#151515" penwidth=0.5];')

    for cluster_name, (node_ids, label, bg, border) in clusters.items():
        lines.append(f'  subgraph {cluster_name} {{')
        if label:
            lines.append(f'    label="{label}";')
            lines.append(f'    fontname="Arial Bold"; fontsize=10; fontcolor="#2a3a6a";')
        lines.append(f'    style=dashed; color="{border}"; bgcolor="{bg}";')
        for nid in node_ids:
            if nid in nodes:
                lines.append(node_dot(nid, nodes[nid]))
        lines.append("  }")
        lines.append("")

    # Edges
    for nid, node in nodes.items():
        if node.get("next"):
            tgt = node["next"]
            taken = nid in path_set and tgt in path_set
            c, pw = ("#FFD700", "2") if taken else ("#0d1730", "0.5")
            lines.append(f'  "{nid}" -> "{tgt}" [color="{c}" penwidth={pw}];')

        for opt in node.get("options", []):
            tgt = opt.get("next")
            if tgt:
                taken = nid in path_set and tgt in path_set
                if taken:
                    lbl_txt = opt["text"][:12] + ("…" if len(opt["text"]) > 12 else "")
                    lines.append(f'  "{nid}" -> "{tgt}" [label="{lbl_txt}" '
                                 f'color="#FFD700" penwidth=1.5 fontcolor="#aaaaaa"];')
                else:
                    lines.append(f'  "{nid}" -> "{tgt}" [color="#0d1020" penwidth=0.3];')

        for cond in node.get("conditions", []):
            tgt = cond.get("goTo") or cond.get("else")
            if tgt:
                taken = nid in path_set and tgt in path_set
                c, pw = ("#FFD700", "1.5") if taken else ("#0d1020", "0.3")
                lines.append(f'  "{nid}" -> "{tgt}" [color="{c}" penwidth={pw} style=dashed];')

    lines.append("}")
    return "\n".join(lines)

# ─── Node renderers ───────────────────────────────────────────────────────────
AXIS_COLORS = {1: ("#3567e8", "AXIS I",   "Locus of Control"),
               2: ("#52b788", "AXIS II",  "Contribution vs Entitlement"),
               3: ("#e8a030", "AXIS III", "Radius of Concern")}

def axis_header(axis_num: int):
    if axis_num not in AXIS_COLORS:
        return
    color, roman, subtitle = AXIS_COLORS[axis_num]
    st.markdown(f"""
    <div style="border-left:3px solid {color};padding:6px 14px;margin-bottom:20px;
                background:rgba(0,0,0,0.25);border-radius:0 6px 6px 0;">
      <span style="color:{color};font-size:10px;font-weight:800;letter-spacing:3px;">{roman}</span>
      <span style="color:#445;font-size:11px;margin-left:10px;">{subtitle}</span>
    </div>""", unsafe_allow_html=True)

def render_start(node, text):
    st.markdown(f"""
    <div style="text-align:center;padding:48px 0 28px;">
      <div style="font-size:56px;margin-bottom:14px;filter:drop-shadow(0 0 20px #2244aa);">🌙</div>
      <h1 style="color:#c5d5ff !important;font-family:Georgia,serif;font-weight:300;
                 font-size:34px;letter-spacing:3px;margin:0 0 6px 0;">Daily Reflection</h1>
      <div style="height:2px;width:80px;background:linear-gradient(90deg,#3567e8,#53d8fb);
                  margin:12px auto 20px;border-radius:2px;"></div>
      <p style="color:#4a5a7a !important;font-size:15px;font-style:italic;max-width:400px;
                margin:0 auto;">{text}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("Begin →", type="primary", use_container_width=True):
            go(node["next"]); st.rerun()

def render_question(node, text, cid):
    axis_header(node.get("axis", 0))
    st.markdown(f"""
    <h2 style="color:#d4d8f0 !important;font-family:Georgia,serif;font-weight:400;
               font-size:21px;line-height:1.55;margin-bottom:24px;">{text}</h2>
    """, unsafe_allow_html=True)
    for i, opt in enumerate(node.get("options", [])):
        if st.button(opt["text"], key=f"o_{cid}_{i}"):
            st.session_state.answers[cid] = {"text": opt["text"], "index": i}
            tally(opt.get("signal", ""))
            go(opt["next"])
            st.rerun()

def render_reflection(node, text, cid):
    axis_num = node.get("axis", 0)
    color = AXIS_COLORS.get(axis_num, ("#52b788",))[0]
    st.markdown(f"""
    <div style="border:1px solid {color}33;border-left:3px solid {color};
                border-radius:0 12px 12px 0;padding:24px 28px;
                background:rgba(10,25,15,0.5);margin:8px 0 24px;">
      <div style="font-size:20px;margin-bottom:14px;opacity:0.9;">💭</div>
      <p style="color:#c8dfc8 !important;font-size:15px;line-height:1.85;
                font-family:Georgia,serif;font-style:italic;margin:0;">{text}</p>
    </div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("Continue →", key=f"c_{cid}", type="primary", use_container_width=True):
            go(node["next"]); st.rerun()

def render_bridge(node, text, cid):
    st.markdown(f"""
    <div style="text-align:center;padding:36px 0;margin:20px 0;
                border-top:1px solid #0f1c30;border-bottom:1px solid #0f1c30;">
      <p style="color:#4a7a90 !important;font-size:14px;font-style:italic;
                letter-spacing:1.5px;margin:0;">— {text} —</p>
    </div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("Continue →", key=f"b_{cid}", type="primary", use_container_width=True):
            go(node["next"]); st.rerun()

def render_summary(node, text, cid):
    st.markdown("""
    <h2 style="color:#ef9a9a !important;font-family:Georgia,serif;font-weight:300;
               letter-spacing:2px;font-size:26px;margin-bottom:8px;">
      Today's Reflection
    </h2>
    <div style="height:1px;background:linear-gradient(90deg,#3a1a1a,transparent);
                margin-bottom:24px;"></div>""", unsafe_allow_html=True)

    # Signal bars
    axes_cfg = [
        ("axis1", "Agency",       "internal",     "external",    "#7eb8ff"),
        ("axis2", "Contribution", "contribution", "entitlement", "#52b788"),
        ("axis3", "Radius",       "altrocentric", "selfcentric", "#e8a030"),
    ]
    for ax_key, label, pos_pole, neg_pole, color in axes_cfg:
        s = st.session_state.signals[ax_key]
        pv, nv = s.get(pos_pole, 0), s.get(neg_pole, 0)
        total  = pv + nv
        pct    = int(pv / total * 100) if total else 50
        dom    = dominant(ax_key)
        st.markdown(f"""
        <div style="margin:14px 0;">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      margin-bottom:6px;">
            <span style="color:{color};font-weight:700;font-size:12px;letter-spacing:1px;">
              {label.upper()}
            </span>
            <span style="color:#3a4a6a;font-size:11px;">{dom} &nbsp;{pct}%</span>
          </div>
          <div style="background:#0a0f1a;border-radius:4px;height:4px;">
            <div style="background:linear-gradient(90deg,{color}99,{color});
                        width:{pct}%;height:4px;border-radius:4px;
                        transition:width 0.5s ease;"></div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    paragraphs = text.split("\n\n")
    box_lines = "".join(
        f'<p style="color:#8a99b8 !important;font-family:Georgia,serif;font-size:14px;'
        f'line-height:1.9;margin:0 0 12px 0;">{p}</p>'
        for p in paragraphs if p.strip()
    )
    st.markdown(f"""
    <div style="background:#060a14;border:1px solid #0f1a2a;border-radius:12px;
                padding:22px 26px;margin-top:4px;">{box_lines}</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("Finish →", key="fin", type="primary", use_container_width=True):
            go(node["next"]); st.rerun()

def render_end(text):
    st.balloons()
    st.markdown(f"""
    <div style="text-align:center;padding:64px 20px;">
      <div style="font-size:52px;margin-bottom:18px;">✨</div>
      <h1 style="color:#c5d5ff !important;font-family:Georgia,serif;font-weight:300;
                 font-size:28px;letter-spacing:3px;">{text}</h1>
    </div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("New Reflection", use_container_width=True, type="primary"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# ─── Main render dispatcher ───────────────────────────────────────────────────
def render(tree: dict):
    nodes = tree["nodes"]
    cid   = st.session_state.current
    node  = nodes[cid]
    ntype = node["type"]

    # Decision nodes are invisible — evaluate and jump
    if ntype == "decision":
        tgt = decide(node)
        if tgt:
            go(tgt)
            st.rerun()
        return

    text = interpolate(node.get("text", ""))

    if ntype == "start":
        render_start(node, text)
    elif ntype == "question":
        render_question(node, text, cid)
    elif ntype == "reflection":
        render_reflection(node, text, cid)
    elif ntype == "bridge":
        render_bridge(node, text, cid)
    elif ntype == "summary":
        render_summary(node, text, cid)
    elif ntype == "end":
        render_end(text)

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    tree = load_tree()
    init()

    # Progress strip
    pct = get_progress()
    st.progress(pct, text=f"  {get_axis_label()}   ·   {int(pct * 100)}%")
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    col_main, col_tree = st.columns([5, 3], gap="large")

    with col_main:
        render(tree)

    with col_tree:
        st.markdown("""
        <p style="color:#1a2a4a;font-size:10px;letter-spacing:3px;
                  text-transform:uppercase;margin-bottom:6px;margin-top:4px;">
          🌳 &nbsp; Reflection Tree
        </p>""", unsafe_allow_html=True)

        dot = build_dot(tree["nodes"], st.session_state.path, st.session_state.current)
        st.graphviz_chart(dot, use_container_width=True)

        # Legend
        st.markdown("""
        <div style="margin-top:10px;font-size:10px;line-height:2;color:#1a2a3a;">
          <div><span style="color:#FFD700;">━━</span>  your path through the tree</div>
          <div><span style="color:#7eb8ff;">■</span>  question &nbsp;
               <span style="color:#ce93d8;">◆</span>  decision &nbsp;
               <span style="color:#a5d6a7;">📄</span>  reflection</div>
          <div><span style="color:#80deea;">▱</span>  bridge &nbsp;
               <span style="color:#ef9a9a;">⬡</span>  summary</div>
        </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()