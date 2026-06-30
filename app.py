import streamlit as st
import subprocess
import pandas as pd
import os

st.title("Redrob Candidate Ranking System")

st.write("""
This sandbox demonstrates the candidate ranking system for Senior AI Engineer role.
Upload a sample candidates file to see ranking in action.
""")

# File upload
uploaded_file = st.file_uploader("Upload candidates JSON file", type=['json', 'jsonl'])

if uploaded_file:
    # Save uploaded file
    with open("candidates_sample.jsonl", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ Uploaded {uploaded_file.name}")
    
    if st.button("Run Ranking"):
        with st.spinner("Ranking candidates (this takes a few seconds)..."):
            # Run the ranking script
            result = subprocess.run(
                ["python", "rank.py", "candidates_sample.jsonl", "output.csv"],
                capture_output=True,
                text=True,
            )
        
        if result.returncode == 0:
            st.success("✅ Ranking Complete!")
            
            # Read and display results
            df = pd.read_csv("output.csv")
            st.write(f"**Top {len(df)} Candidates:**")
            st.dataframe(df)
            
            # Download button
            csv_content = open("output.csv").read()
            st.download_button(
                label="Download Results CSV",
                data=csv_content,
                file_name="ranking_results.csv",
                mime="text/csv"
            )
        else:
            st.error("Ranking failed!")

st.write("### Return Code")
st.code(result.returncode)

st.write("### Standard Output")
st.code(result.stdout)

st.write("### Error Output")
st.code(result.stderr)

st.write("---")
st.write("**How it works:**")
st.write("""
1. Upload a JSON/JSONL file with candidate data
2. System scores candidates on:
   - Title Match (30%)
   - Skills Match (25%)
   - Experience (20%)
   - Education (10%)
   - Behavioral Signals (15%)
3. Returns top 100 ranked candidates
""")
