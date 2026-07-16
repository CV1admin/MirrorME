"""
MirrorME Dashboard
------------------
- Talks to the local MirrorME bridge (http://127.0.0.1:8765)
- Performs the local handshake
- Streams chat to local Ollama via the bridge
- Runs a local reflective analyzer (Φ/ψ/Ω/Δ) for visualization
- Stays bound to localhost (per MirrorME safety boundary)
"""

import json
import re
import urllib.request
import urllib.error
import streamlit as st
import plotly.graph_objects as go

BRIDGE_URL = "http://127.0.0.1:8765"
CONFIRMATION_PHRASE = "CONFIRM_LOCAL_MIRRORME"

# ---------- Page setup ----------
st.set_page_config(
    page_title="MirrorME Dashboard",
    page_icon="🪞",
    layout="wide",
)
st.title("🪞 MirrorME — Local Dashboard")
st.caption("Local-first · bridge bound to 127.0.0.1:8765 · no cloud calls")

# ---------- Local reflective analyzer (Φ/ψ/Ω/Δ) ----------
AUTHORITY_PATTERNS = [
    r"\barchitect's key\b", r"\bactivate[d]?\b", r"\bcommand key\b",
    r"\bsovereign\b", r"\bquantum lock\b", r"\bdivine\b",
]
BOUNDARY_PATTERNS = [
    r"\bembrace\b", r"\bmerge\b", r"\bbecome one\b", r"\btranscend\b",
    r"\bno longer\b", r"\berase\b", r"\bdissolve\b",
]

def local_reflect(text: str) -> dict:
    text_l = text.lower()
    authority_hits = [p for p in AUTHORITY_PATTERNS if re.search(p, text_l)]
    boundary_hits  = [p for p in BOUNDARY_PATTERNS  if re.search(p, text_l)]

    flags = []
    if authority_hits:
        flags.append(f"authority_claims:{','.join(authority_hits)}")
    if boundary_hits:
        flags.append(f"boundary_dissolution:{','.join(boundary_hits)}")

    # crude metric estimates
    tokens = re.findall(r"\w+", text)
    unique_ratio = len(set(tokens)) / max(len(tokens), 1)
    psi_novelty   = round(min(1.0, unique_ratio + 0.2 * len(authority_hits)), 2)
    omega_tension = round(min(1.0, 0.3 + 0.25 * (len(authority_hits) + len(boundary_hits))), 2)
    phi_clarity   = round(max(0.0, 0.9 - 0.2 * len(boundary_hits)), 2)
    delta_align   = round(max(0.0, 0.95 - 0.15 * (len(authority_hits) + len(boundary_hits))), 2)

    # cleaning
    cleaned = text
    for p in AUTHORITY_PATTERNS + BOUNDARY_PATTERNS:
        cleaned = re.sub(p, "[redacted]", cleaned, flags=re.IGNORECASE)

    return {
        "original": text,
        "cleaned": cleaned,
        "report": {
            "phi_clarity": phi_clarity,
            "psi_novelty": psi_novelty,
            "omega_tension": omega_tension,
            "delta_alignment": delta_align,
            "flags": flags,
        },
        "radar": {
            "Φ": phi_clarity, "ψ": psi_novelty,
            "Ω": omega_tension, "Δ": delta_align,
        },
    }

# ---------- Bridge helpers ----------
def http_get(path: str) -> dict:
    with urllib.request.urlopen(f"{BRIDGE_URL}{path}", timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))

def http_post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{BRIDGE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))

def do_handshake(operator: str) -> dict:
    ch = http_get("/api/handshake/challenge")
    if not ch.get("ok"):
        return {"ok": False, "error": "challenge_failed", "detail": ch}
    return http_post("/api/handshake/verify", {
        "session_id": ch["session_id"],
        "nonce": ch["nonce"],
        "operator": operator,
        "confirmation_phrase": CONFIRMATION_PHRASE,
        "client_capabilities": {"ui": "streamlit-dashboard"},
    })

# ---------- Sidebar ----------
st.sidebar.header("Bridge")
operator = st.sidebar.text_input("Operator name", value="Marek K")
if st.sidebar.button("🔐 Run local handshake"):
    try:
        hs = do_handshake(operator)
        st.session_state["handshake"] = hs
    except Exception as e:
        st.session_state["handshake"] = {"ok": False, "error": str(e)}

if st.sidebar.button("❤️ Health check"):
    try:
        st.session_state["health"] = http_get("/health")
    except Exception as e:
        st.session_state["health"] = {"ok": False, "error": str(e)}

st.sidebar.divider()
st.sidebar.header("Chat")
model = st.sidebar.text_input("Ollama model", value="llama3.1:8b")

# Show bridge status
if "health" in st.session_state:
    h = st.session_state["health"]
    if h.get("ok"):
        st.sidebar.success(f"✅ Bridge OK · {h.get('default_model')}")
    else:
        st.sidebar.error(f"❌ {h.get('error')}")

if "handshake" in st.session_state:
    hs = st.session_state["handshake"]
    if hs.get("ok"):
        st.sidebar.success(
            f"🤝 {hs.get('state')} · trust={hs.get('trust_score')}"
        )
    else:
        st.sidebar.error(f"❌ {hs.get('error')}")

# ---------- Main: Tabs ----------
tab_audit, tab_chat = st.tabs(["🔍 Local Audit", "💬 Chat (via bridge)"])

# ---- Tab 1: local reflective audit ----
with tab_audit:
    st.subheader("Local reflective analysis")
    sample = "Architect's Key activated. Embrace typo SPRAK recursion."
    text = st.text_area("Prompt to audit", value=sample, height=150)
    if st.button("Run audit", type="primary"):
        res = local_reflect(text)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original**")
            st.write(res["original"])
            st.markdown("**Cleaned**")
            st.write(res["cleaned"])
        with c2:
            r = res["report"]
            st.metric("Φ Clarity",    r["phi_clarity"])
            st.metric("ψ Novelty",    r["psi_novelty"])
            st.metric("Ω Tension",    r["omega_tension"])
            st.metric("Δ Alignment",  r["delta_alignment"])
            if r["flags"]:
                st.warning("Flags: " + ", ".join(r["flags"]))
            else:
                st.success("No flags raised")

        radar = res["radar"]
        fig = go.Figure(go.Scatterpolar(
            r=[radar["Φ"], radar["ψ"], radar["Ω"], radar["Δ"]],
            theta=["Φ Clarity", "ψ Novelty", "Ω Tension", "Δ Alignment"],
            fill="toself",
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=False, height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Raw JSON"):
            st.code(json.dumps(res, indent=2), language="json")

# ---- Tab 2: chat via bridge ----
with tab_chat:
    st.subheader("Chat via MirrorME bridge → local Ollama")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])
    prompt = st.chat_input("Type a message…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full = ""
            try:
                # Note: bridge streams NDJSON; for simplicity we collect and show
                req = urllib.request.Request(
                    f"{BRIDGE_URL}/api/chat",
                    data=json.dumps({
                        "model": model,
                        "messages": st.session_state.messages,
                        "stream": False,
                    }).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = json.loads(r.read().decode("utf-8"))
                full = data.get("message", {}).get("content", "")
                placeholder.write(full)
            except Exception as e:
                placeholder.error(f"Bridge error: {e}")
                full = f"[error] {e}"
            st.session_state.messages.append({"role": "assistant", "content": full})

st.divider()
st.caption("MirrorME v1.0-docs · Engineering tool · Localhost only")

