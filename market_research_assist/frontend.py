import streamlit as st
import subprocess
import sys
from pathlib import Path

st.title("Social Data Sentiment Analysis")

tag = st.text_input("Enter a tag to fetch and analyze social data:")

if st.button("Run Analysis"):
    if not tag:
        st.warning("Please enter a tag.")
    else:
        st.info("Running backend pipeline. This may take a while...")
        # Call your core.py script with the tag
        core_py = Path(__file__).parent / "core.py"
        result = subprocess.run(
            [sys.executable, str(core_py), tag],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Parse and display sentiment results from stdout
            output = result.stdout
            st.success("Pipeline completed!")
            st.text_area("Pipeline Output", output, height=300)
        else:
            st.error("Pipeline failed!")
            st.text_area("Error Output", result.stderr, height=300)