import streamlit as st
import subprocess
import pandas as pd
import os

st.set_page_config(page_title="Redrob Candidate Ranking System", layout="wide")

st.title("Redrob Candidate Ranking System")

st.write("""
This sandbox demonstrates the candidate ranking system for the Senior AI Engineer role.
Upload a sample candidates file to see the ranking in action.
""")

# File Upload
uploaded_file = st.file_uploader(
    "Upload candidates JSON/JSONL file",
    type=["json", "jsonl"]
)

if uploaded_file is not None:

    # Save uploaded file
    input_file = "candidates_sample.jsonl"

    with open(input_file, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ Uploaded {uploaded_file.name}")

    if st.button("Run Ranking"):

        with st.spinner("Ranking candidates..."):

            result = subprocess.run(
                ["python", "rank.py", input_file, "output.csv"],
                capture_output=True,
                text=True
            )

        if result.returncode == 0:

            st.success("✅ Ranking Complete!")

            df = pd.read_csv("output.csv")

            st.subheader("Top Ranked Candidates")

            st.dataframe(df, use_container_width=True)

            st.download_button(
                label="📥 Download Results",
                data=df.to_csv(index=False),
                file_name="ranking_results.csv",
                mime="text/csv"
            )

        else:
            st.error(result.stderr)

st.divider()

st.subheader("How it Works")

st.markdown("""
1. Upload a JSON/JSONL file containing candidate profiles.
2. The system evaluates each candidate based on:
   - **Title Match (30%)**
   - **Skills Match (25%)**
   - **Experience (20%)**
   - **Education (10%)**
   - **Behavioral Signals (15%)**
3. Candidates are ranked by their overall score.
4. The top-ranked candidates are displayed and can be downloaded as a CSV file.
""")
