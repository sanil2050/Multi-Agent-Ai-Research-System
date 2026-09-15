"""
Streamlit UI for the multi-agent research pipeline.

Place this file in the same folder as pipeline.py (and agents.py) and run:
    streamlit run app.py
"""

import io
import sys
import traceback
from datetime import datetime

import streamlit as st

from pipeline import run_research_pipeline


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def to_text(x) -> str:
    """Best-effort conversion of a chain/agent result into plain text.
    Handles LangChain message objects (which expose `.content`) as well
    as plain strings."""
    if x is None:
        return ""
    if hasattr(x, "content"):
        return x.content
    return str(x)


class StreamlitLogger(io.StringIO):
    """Redirects stdout into a Streamlit placeholder so the terminal
    prints already in pipeline.py show up live in the UI."""

    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.buffer = ""

    def write(self, s):
        self.buffer += s
        # keep the box from growing forever
        self.placeholder.code(self.buffer[-4000:], language="text")
        return len(s)

    def flush(self):
        pass


# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔎",
    layout="wide",
)

if "history" not in st.session_state:
    st.session_state.history = []


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    st.title("🔎 Research Pipeline")
    st.markdown(
        "A multi-agent system that **searches**, **reads**, **writes**, "
        "and **critiques** a report on any topic you give it."
    )
    st.markdown("---")
    st.markdown("**Pipeline stages**")
    st.markdown(
        "1. 🔍 **Research Agent** — searches the web\n"
        "2. 📖 **Reader Agent** — scrapes the best source\n"
        "3. ✍️ **Writer** — drafts the report\n"
        "4. 🧐 **Critic** — reviews the draft"
    )
    st.markdown("---")
    show_logs = st.checkbox("Show live agent logs", value=True)
    if st.session_state.history:
        st.markdown("---")
        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.rerun()


# --------------------------------------------------------------------------
# Main - input
# --------------------------------------------------------------------------

st.title("Multi-Agent Research Assistant")
st.caption("Give it a topic. Get a researched, written, and critiqued report.")

topic = st.text_input(
    "Research topic",
    placeholder="e.g. The impact of quantum computing on cryptography",
)

run_clicked = st.button("Run research", type="primary")

if run_clicked:
    if not topic.strip():
        st.warning("Enter a topic first.")
    else:
        result = None
        error = None
        old_stdout = sys.stdout

        with st.status("Running multi-agent pipeline...", expanded=True) as status:
            log_placeholder = st.empty()
            if show_logs:
                sys.stdout = StreamlitLogger(log_placeholder)
            try:
                result = run_research_pipeline(topic)
                status.update(label="Pipeline complete ✅", state="complete")
            except Exception as e:
                error = e
                traceback.print_exc()
                status.update(label="Pipeline failed ❌", state="error")
            finally:
                sys.stdout = old_stdout

        if error:
            st.error(f"Pipeline failed: {error}")
            with st.expander("Traceback"):
                st.code("".join(traceback.format_exception(error)), language="text")
        elif result:
            st.session_state.history.insert(
                0,
                {
                    "topic": topic,
                    "result": result,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                },
            )
            st.rerun()


# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------

if st.session_state.history:
    latest = st.session_state.history[0]
    st.markdown("## Results")
    st.subheader(f"📌 {latest['topic']}")
    st.caption(f"Run at {latest['time']}")

    report_text = to_text(latest["result"].get("report"))
    critique_text = to_text(latest["result"].get("critique"))
    search_text = to_text(latest["result"].get("search_results"))
    scraped_text = to_text(latest["result"].get("scraped_content"))

    tab_report, tab_critique, tab_search, tab_scraped = st.tabs(
        ["📄 Report", "🧐 Critique", "🔍 Search Results", "📖 Scraped Content"]
    )

    with tab_report:
        st.markdown(report_text or "_No report generated._")
        if report_text:
            st.download_button(
                "Download report as .md",
                data=report_text,
                file_name=f"report_{latest['topic'][:30].replace(' ', '_')}.md",
                mime="text/markdown",
            )

    with tab_critique:
        st.markdown(critique_text or "_No critique generated._")

    with tab_search:
        st.text_area("Search results", search_text, height=300, label_visibility="collapsed")

    with tab_scraped:
        st.text_area("Scraped content", scraped_text, height=300, label_visibility="collapsed")

    if len(st.session_state.history) > 1:
        with st.expander(f"Previous runs ({len(st.session_state.history) - 1})"):
            for i, item in enumerate(st.session_state.history[1:], start=1):
                st.markdown(f"**{item['topic']}** — {item['time']}")
                if st.button("View", key=f"view_{i}"):
                    st.session_state.history.insert(
                        0, st.session_state.history.pop(i)
                    )
                    st.rerun()
                st.markdown("---")
else:
    st.info("Run a topic above to see results here.")
    