# pages/0_Debug_Syntax.py
import streamlit as st, ast, io, traceback

st.title("🔎 Syntax Debugger")

TARGETS = [
    "pages/1_📊_Executive_Overview.py",
    "pages/2_📈_Channel_Performance.py",
    "pages/5_⚙️_Settings.py",
    "utils/visualizations.py",
]

def show_ctx(src, lineno, radius=4):
    lines = src.splitlines()
    start = max(lineno - radius - 1, 0)
    end = min(lineno + radius, len(lines))
    code = "\n".join(f"{i+1:>4} | {lines[i]}" for i in range(start, end))
    st.code(code, language="python")

for path in TARGETS:
    st.subheader(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        ast.parse(src, filename=path, mode="exec")
        st.success("✅ No syntax errors")
    except SyntaxError as e:
        st.error(f"❌ SyntaxError: {e.msg}  (line {e.lineno}, col {e.offset})")
        show_ctx(src, e.lineno)
    except Exception as e:
        st.warning(f"⚠️ Other error while checking: {e}")
