"""
streamlit_app.py
"""
import sys
import os

# Force correct venv path
current_dir = os.path.dirname(os.path.abspath(__file__))
venv_packages = os.path.join(current_dir, "venv", "Lib", "site-packages")
if venv_packages not in sys.path:
    sys.path.insert(0, venv_packages)
sys.path.insert(0, current_dir)

import streamlit as st
st.set_page_config(
    page_title="Cyber Security LLM Agents",
    page_icon="🛡️",
    layout="wide",
)

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .title-style { color: #00ff41; font-size: 2.5rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-style">🛡️ Cyber Security LLM Agents</p>', unsafe_allow_html=True)
st.markdown("**AI-powered multi-agent framework for cybersecurity research**")
st.divider()

# ── Load API key from secrets (hidden from users) ─────────────────────────────
groq_api_key = ""
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    groq_api_key = os.getenv("GROQ_API_KEY", "")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    model = st.selectbox(
    "🤖 Select Model",
    options=[
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
    ],
    index=0,
)

    agent_type = st.selectbox(
        "🕵️ Select Agent",
        options=["text", "code", "coord"],
        format_func=lambda x: {
            "text": "📝 Text Agent — Explain & Report",
            "code": "💻 Code Agent — Execute Commands",
            "coord": "🎯 Coordinator — Full Engagement",
        }[x]
    )

    st.divider()
    st.markdown("### 📖 Agent Info")
    agent_info = {
        "text": "Answers questions, explains techniques, writes security reports.",
        "code": "Autonomously runs shell commands and Python code to complete tasks.",
        "coord": "Orchestrates all agents together for complex multi-step tasks.",
    }
    st.info(agent_info[agent_type])

    st.divider()
    st.markdown("### 💡 Example Tasks")
    examples = {
        "text": [
            "Explain SQL injection and how to prevent it",
            "Explain the MITRE ATT&CK framework",
            "Write a penetration testing report template",
            "Explain how ransomware works",
            "What are the top 10 OWASP vulnerabilities?",
        ],
        "code": [
            "Check Python version installed",
            "List all files in current directory",
        ],
        "coord": [
            "Perform web recon on http://testphp.vulnweb.com and write a report",
        ],
    }
    for ex in examples[agent_type]:
        if st.button(f"▶ {ex}", use_container_width=True):
            st.session_state["task_input"] = ex

# ── Main Area ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Task Input")
    task = st.text_area(
        "Enter your security task:",
        value=st.session_state.get("task_input", ""),
        height=150,
        placeholder="e.g. Explain what SQL injection is",
        key="task_input",
    )
    run_button = st.button("🚀 Run Agent", type="primary", use_container_width=True)

with col2:
    st.subheader("ℹ️ Status")
    if not groq_api_key:
        st.error("⚠️ API Key not configured. Contact admin.")
    else:
        st.success(f"✅ Ready | Model: `{model}` | Agent: `{agent_type}`")
        st.info("Enter a task on the left and click Run Agent")

# ── Run Agent ─────────────────────────────────────────────────────────────────
if run_button:
    if not groq_api_key:
        st.error("❌ API Key not configured!")
    elif not task.strip():
        st.error("❌ Please enter a task!")
    else:
        os.environ["GROQ_API_KEY"] = groq_api_key
        os.environ["LLM_MODEL"] = model

        st.divider()
        st.subheader("🤖 Agent Output")

        with st.spinner("🔄 Running agent... Please wait..."):
            try:
                if agent_type == "text":
                    from agents.text_agents import TextAgent
                    agent = TextAgent(model=model)
                    result = agent.run(task)
                elif agent_type == "code":
                    from agents.code_agents import CodeAgent
                    agent = CodeAgent(model=model)
                    result = agent.run(task)
                elif agent_type == "coord":
                    from agents.coordinator_agents import CoordinatorAgent
                    agent = CoordinatorAgent(model=model)
                    result = agent.run(task)

                st.markdown(result)
                st.divider()
                st.download_button(
                    label="📥 Download Report",
                    data=result,
                    file_name="security_report.md",
                    mime="text/markdown",
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.code(str(e))

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(" 🛡️ **Cyber Security AI-Agents**  | ⚠️ For educational use only")