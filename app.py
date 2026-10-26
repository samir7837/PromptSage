"""PromptSage: a local, rule-based NLP prompt reviewer."""

import json
import streamlit as st
import streamlit.components.v1 as components

from nlp_analyzer import analyze_prompt
from optimizer import optimize_prompt
from token_counter import SUPPORTED_ENCODINGS, compare_prompts, count_tokens, get_encoding

st.set_page_config(page_title="PromptSage", page_icon="✦", layout="wide")
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp, [data-testid="stAppViewContainer"] { background: #0b1220; color: #e5edf8; }
[data-testid="stHeader"] { background: rgba(11,18,32,.92); }
[data-testid="stSidebar"] { background: #101a2b; border-right: 1px solid #243248; }
.block-container { max-width: 1180px; padding-top: 2.2rem; }
.stMarkdown, .stMarkdown p, .stMarkdown li, label, [data-testid="stCaptionContainer"] { color: #c5d1e0; }
h1, h2, h3, [data-testid="stSubheader"] { color: #f1f5fb !important; }
[data-testid="stMetric"] { background: #121e30; border: 1px solid #283951; padding: 16px 18px; border-radius: 14px; }
[data-testid="stMetricLabel"] p { color: #a9bad0 !important; }
[data-testid="stMetricValue"] { color: #f1f5fb !important; }
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input { background: #111c2d; color: #edf3fb; border-color: #35465e; }
[data-testid="stSelectbox"] div[data-baseweb="select"] > div { background: #111c2d; color: #edf3fb; border-color: #35465e; }
[data-baseweb="popover"] { background: #142136; }
[data-baseweb="popover"] * { color: #e5edf8; }
[data-testid="stExpander"] { background: #111c2d; border: 1px solid #283951; border-radius: 12px; }
[data-testid="stExpander"] summary { color: #e5edf8; }
.stButton button[kind="secondary"] { background: #17253a; color: #e5edf8; border: 1px solid #3a4d66; }
.stButton button[kind="primary"] { background: #497fe0; color: white; border: 0; }
.hero { padding: 1.5rem 1.8rem; border-radius: 18px; color: white; background: linear-gradient(120deg,#162b4d,#3265a8); margin-bottom: 1.4rem; }
.hero h1 { color: white !important; }
.hero p { color: #dce8fa; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>✦ PromptSage</h1><p>Write smarter prompts. Use fewer tokens.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("About PromptSage")
    st.write("A local NLP project that reviews prompt structure and applies transparent, rule-based cleanup.")
    st.subheader("NLP techniques")
    st.markdown("- Text normalization and word tokenization\n- Stopword filtering for keywords\n- Frequency counts and phrase matching\n- Deterministic rule-based optimization")
    st.subheader("Tokenization")
    st.caption("The selected tiktoken encoding performs subword tokenization (BPE). Exact counts apply to that encoding; different AI models may use different tokenizers.")

SAMPLES = {
    "Clear explanation": "Can you please explain how photosynthesis works in a very simple way? Include the main stages and one example.",
    "Constrained summary": "I would like you to summarize the causes of the French Revolution in 150 words. Use three bullet points and include the years 1789 and 1799.",
    "Code request": "Could you please write a Python function to check whether a number is prime? Include input validation and two example tests.",
}
sample = st.selectbox("Try a sample prompt (optional)", ["Choose a sample…", *SAMPLES])
if sample != "Choose a sample…" and st.session_state.get("last_sample") != sample:
    st.session_state.prompt_input = SAMPLES[sample]
st.session_state.last_sample = sample
prompt = st.text_area("Your prompt", key="prompt_input", height=190, placeholder="Paste or write a prompt to analyze…")
encoding = st.selectbox("Token encoding", SUPPORTED_ENCODINGS, help="Counts are exact for the selected tiktoken encoding only.")
left, right, _ = st.columns([1, 1, 5])
analyze_clicked = left.button("Analyze Prompt", type="primary", use_container_width=True)
reset_clicked = right.button("Reset", use_container_width=True)
if reset_clicked:
    for key in ("prompt_input", "analysis", "optimized_prompt", "last_sample"):
        st.session_state.pop(key, None)
    st.rerun()

if analyze_clicked:
    if not prompt.strip():
        st.warning("Enter a prompt before analyzing.")
    elif not any(ch.isalnum() for ch in prompt):
        st.warning("This input contains no words to analyze. Add some text and try again.")
    else:
        try:
            get_encoding(encoding)
            st.session_state.analysis = analyze_prompt(prompt)
            st.session_state.original_prompt = prompt
            st.session_state.encoding_used = encoding
            st.session_state.optimized_prompt = optimize_prompt(prompt)
        except Exception as exc:
            st.error(f"Could not initialize {encoding}: {exc}")

if st.session_state.get("analysis"):
    data = st.session_state.analysis
    original = st.session_state.original_prompt
    active_encoding = st.session_state.encoding_used
    try:
        original_tokens = count_tokens(original, active_encoding)
    except Exception as exc:
        st.error(f"Token counting failed: {exc}")
    else:
        st.subheader("Prompt snapshot")
        cols = st.columns(4)
        metrics = [("Characters", data["characters"]), ("Words", data["words"]), ("Sentences", data["sentences"]), ("Tokens", original_tokens)]
        for col, (label, value) in zip(cols, metrics): col.metric(label, value)
        cols = st.columns(4)
        for col, (label, value) in zip(cols, [("Unique words", data["unique_words"]), ("Reading time", f"{data['reading_time_minutes']:.1f} min"), ("Avg. words / sentence", f"{data['average_words_per_sentence']:.1f}"), ("Encoding", active_encoding)]): col.metric(label, value)

        st.subheader("Rule-based optimization")
        st.caption("Review and edit the suggested text before using it. Rule-based edits can change meaning; check all constraints and details.")
        st.text_area("Editable optimized prompt", key="optimized_prompt", height=150)
        optimized = st.session_state.optimized_prompt
        comparison = compare_prompts(original, optimized, active_encoding)
        if optimized == original:
            st.info("No obvious rule-based optimization was found.")
        elif comparison["tokens_saved"] > 0:
            st.success(f"The current draft saves {comparison['tokens_saved']} tokens with {active_encoding}.")
        elif comparison["tokens_saved"] < 0:
            st.warning(f"The current draft uses {abs(comparison['tokens_saved'])} more tokens with {active_encoding}.")
        else:
            st.info("The draft changes the text without changing its token count.")
        a, b = st.columns(2)
        with a:
            st.markdown("**Original**")
            st.code(original, language=None)
        with b:
            st.markdown("**Optimized draft**")
            st.code(optimized, language=None)
        st.caption(f"Words: {comparison['original_words']} → {comparison['optimized_words']} · Characters reduced: {comparison['character_reduction']}")
        st.progress(min(max(comparison["reduction_percentage"], 0) / 100, 1.0), text=f"Token reduction: {comparison['reduction_percentage']:.1f}% (negative values indicate an increase)")
        prompt_json = json.dumps(optimized).replace("</", "<\\/")
        components.html(f"""
        <button id="copy-prompt" style="border:0;border-radius:8px;padding:9px 14px;background:#3265a8;color:white;font-weight:600;cursor:pointer">Copy Optimized Prompt</button>
        <span id="copy-status" style="margin-left:10px;font:13px sans-serif;color:#26734d"></span>
        <script>
        const promptText = {prompt_json};
        document.getElementById('copy-prompt').addEventListener('click', async () => {{
          const status = document.getElementById('copy-status');
          try {{ await navigator.clipboard.writeText(promptText); status.textContent = 'Copied'; }}
          catch (_) {{ status.textContent = 'Clipboard unavailable; select and copy the text above.'; }}
        }});
        </script>
        """, height=44)

        with st.expander("NLP Insights", expanded=False):
            st.markdown("**Text normalization:** comparisons use case-folded words; punctuation is excluded from word counts. The original prompt remains unchanged.\n\n**Word tokenization:** NLTK's resource-free Treebank tokenizer splits text into word-like units.\n\n**Stopword filtering:** a compact English stopword list is used only for keyword analysis. Stopwords stay in your prompt.\n\n**Word-frequency distribution:** counts show frequent meaningful words after stopword filtering.")
            if data["frequent_words"]:
                st.table({"Word": [x[0] for x in data["frequent_words"]], "Frequency": [x[1] for x in data["frequent_words"]]})
            else:
                st.write("No meaningful keywords found.")
            st.markdown("**Filler phrase detection:** checks a small list of configurable phrase patterns.")
            st.write(", ".join(data["filler_phrases"]) if data["filler_phrases"] else "No configured filler phrases detected.")
            st.markdown("**Repeated words:**")
            st.write(data["repeated_words"] or "No repeated words detected.")
            st.markdown("**Rule-based transformation:** removes or shortens selected verbose patterns and normalizes whitespace. It is deterministic, not a trained machine-learning model, and cannot guarantee semantic preservation.\n\n**BPE tokenization:** tiktoken breaks text into encoding-specific subword pieces. Whitespace-separated words and model tokens are different units: one word can map to several tokens, and punctuation or Unicode can also affect token boundaries.")

