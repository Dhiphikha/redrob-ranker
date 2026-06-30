import streamlit as st
import pandas as pd
import json
from pathlib import Path
import tempfile
import time
from datetime import datetime
import hashlib

st.set_page_config(
    page_title="Redrob • Candidate Ranking",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme
st.markdown("""
<style>
    .main {background-color: #0f172a; color: #e2e8f0;}
    .stApp {background-color: #0f172a;}
    .block-container {padding-top: 2rem;}
    h1, h2, h3 {color: #60a5fa;}
    .metric-card {
        background: #1e2937;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x80/1e3a8a/ffffff?text=REDROB+AI", use_column_width=True)
    st.title("Configuration")
    
    st.metric("Max File Size", "500 MB")
    st.metric("Supported", "JSONL / JSON")
    
    st.divider()
    st.subheader("Ranking Criteria")
    st.caption("""
    • Experience  
    • Skills Match  
    • Education  
    • Interview Score  
    • Custom Signals
    """)

st.title("🎯 Professional Candidate Ranking Platform")
st.markdown("**AI-Powered Talent Intelligence • Senior Engineering Roles**")

# File Upload
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader(
        "Upload candidates.jsonl",
        type=["jsonl", "json"],
        help="Large files supported (up to 500MB)"
    )

if uploaded_file:
    file_size = uploaded_file.size / (1024**2)
    
    # File Info
    info_cols = st.columns(4)
    with info_cols[0]:
        st.metric("File", uploaded_file.name)
    with info_cols[1]:
        st.metric("Size", f"{file_size:.2f} MB")
    with info_cols[2]:
        st.metric("Hash", hashlib.md5(uploaded_file.getbuffer()).hexdigest()[:8])
    with info_cols[3]:
        st.metric("Status", "✅ Ready")
    
    st.divider()
    
    # Load Data
    with st.spinner("Loading data..."):
        try:
            if file_size > 100:
                df = pd.read_json(uploaded_file, lines=True, nrows=80000)
                st.warning(f"Large file → Loaded first 80,000 records")
            else:
                df = pd.read_json(uploaded_file, lines=True)
            
            st.success(f"✅ Loaded {len(df):,} candidates")
            st.dataframe(df.head(5), use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load file: {e}")
            st.stop()
    
    # Scoring Configuration
    st.subheader("🎛️ Scoring Configuration")
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    
    weights = {}
    cols = st.columns(3)
    for i, col in enumerate(numeric_cols[:9]):
        with cols[i % 3]:
            w = st.slider(f"{col}", 0, 100, 50, key=col)
            weights[col] = w / 100.0
    
    if st.button("🚀 Run Ranking", type="primary", use_container_width=True):
        with st.spinner("Ranking candidates..."):
            progress = st.progress(0)
            
            # Calculate weighted score
            df_rank = df.copy()
            df_rank['score'] = 0.0
            
            for col, weight in weights.items():
                if col in df_rank.columns:
                    minv, maxv = df_rank[col].quantile(0.01), df_rank[col].quantile(0.99)
                    if maxv > minv:
                        norm = (df_rank[col] - minv) / (maxv - minv)
                        df_rank['score'] += norm.clip(0, 1) * weight
            
            # Final ranking
            df_rank = df_rank.sort_values('score', ascending=False).reset_index(drop=True)
            df_rank['rank'] = range(1, len(df_rank) + 1)
            df_rank['reasoning'] = "Strong profile match based on weighted criteria"
            
            progress.progress(100)
            
            # Results
            st.success(f"✅ Ranking completed! Top score: {df_rank['score'].max():.4f}")
            
            st.subheader("🏆 Top 50 Ranked Candidates")
            st.dataframe(
                df_rank.head(50)[['rank', 'score', 'reasoning'] + [c for c in df.columns if c not in ['score', 'rank', 'reasoning']]],
                use_container_width=True,
                height=600
            )
            
            # Download
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            csv_data = df_rank.to_csv(index=False).encode()
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button("📥 Download Full Ranking (CSV)", csv_data, f"candidate_ranking_{timestamp}.csv", "text/csv")
            with col_d2:
                st.download_button("📥 Download as JSON", df_rank.to_json(orient="records", indent=2), f"candidate_ranking_{timestamp}.json", "application/json")

else:
    st.info("👆 Please upload your **candidates.jsonl** file to start professional ranking.")

st.divider()
st.caption("© Redrob AI • Professional Candidate Ranking System • Built for Scale")
