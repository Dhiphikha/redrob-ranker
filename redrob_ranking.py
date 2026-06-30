import streamlit as st
import subprocess
import pandas as pd
import os
import tempfile
import time
from datetime import datetime
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Redrob Candidate Ranking",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Dark professional theme, no white spaces
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
        padding: 2rem;
    }
    .stApp {
        background-color: #0e1117;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #374151;
    }
    h1, h2, h3 {
        color: #60a5fa;
    }
    .stButton>button {
        background-color: #ef4444;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #f87171;
    }
    .dataframe {
        background-color: #1f2937;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/280x80/1e40af/ffffff?text=REDROB+AI", use_column_width=True)
    
    st.header("⚙️ Configuration")
    
    st.subheader("System Specs")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Max File Size", "500 MB")
    with col2:
        st.metric("Timeout", "5 min")
    
    st.divider()
    
    st.subheader("📊 Processing Info")
    st.info("""
    **Supported Formats:**
    - JSON (.json)
    - JSONL (.jsonl)
    
    **Output:**
    - Top ranked candidates
    - CSV + JSON download
    - Detailed metrics
    """)
    
    st.divider()
    
    st.subheader("🔧 Ranking Logic")
    st.caption("""
    **Weights:**
    - Title Match: 30%
    - Skills Match: 25%
    - Experience: 20%
    - Education: 10%
    - Other Signals: 15%
    """)

# Main Content - Dark Theme
st.title("🎯 Redrob Candidate Ranking System")
st.markdown("**Professional AI-powered ranking for technical roles**")

st.divider()

# File Upload
st.header("📤 Upload Candidate Data")
uploaded_file = st.file_uploader(
    "Select your candidates.jsonl (or .json)",
    type=['json', 'jsonl'],
    help="Large files supported (up to 500MB)"
)

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    if file_size_mb > 500:
        st.error(f"File too large ({file_size_mb:.1f} MB). Max 500 MB.")
    else:
        # File info cards
        cols = st.columns(4)
        with cols[0]:
            st.metric("📄 File Name", uploaded_file.name[:25] + "..." if len(uploaded_file.name) > 25 else uploaded_file.name)
        with cols[1]:
            st.metric("💾 Size", f"{file_size_mb:.2f} MB")
        with cols[2]:
            file_hash = hashlib.md5(uploaded_file.getbuffer()).hexdigest()[:8]
            st.metric("🔐 Hash", file_hash)
        with cols[3]:
            st.metric("✅ Status", "Ready", delta="Valid")
        
        st.divider()
        
        # Processing Options
        st.subheader("⚙️ Processing Options")
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            show_preview = st.checkbox("Show file preview", value=True)
        with col_opt2:
            validate_data = st.checkbox("Validate data", value=True)
        
        if st.button("🚀 Start Ranking", type="primary", use_container_width=True):
            progress_container = st.container()
            results_container = st.container()
            
            with progress_container:
                st.subheader("📈 Processing Progress")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Save file
                    status_text.info("💾 Saving uploaded file...")
                    progress_bar.progress(20)
                    
                    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl', mode='wb')
                    temp_input.write(uploaded_file.getbuffer())
                    temp_input.close()
                    
                    # Step 2: Validate
                    if validate_data:
                        status_text.info("🔍 Validating data...")
                        progress_bar.progress(45)
                        # Quick validation
                        with open(temp_input.name, 'r', encoding='utf-8') as f:
                            line_count = sum(1 for _ in f)
                    
                    # Step 3: Run ranking
                    status_text.info("🔄 Running AI Ranking...")
                    progress_bar.progress(70)
                    
                    rank_start = time.time()
                    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
                    output_path = temp_output.name
                    temp_output.close()
                    
                    result = subprocess.run(
                        ["python", "rank.py", temp_input.name, output_path],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode != 0:
                        st.error(f"Ranking error: {result.stderr}")
                    else:
                        # Load results
                        df = pd.read_csv(output_path)
                        
                        progress_bar.progress(100)
                        status_text.success("✅ Ranking Complete!")
                        
                        # Results
                        with results_container:
                            st.divider()
                            st.subheader("🏆 Ranking Results")
                            
                            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                            with mcol1:
                                st.metric("Candidates Processed", len(df))
                            with mcol2:
                                st.metric("Top Score", f"{df['score'].max():.4f}" if 'score' in df.columns else "N/A")
                            with mcol3:
                                st.metric("Avg Score", f"{df['score'].mean():.4f}" if 'score' in df.columns else "N/A")
                            with mcol4:
                                st.metric("Time Taken", f"{time.time() - rank_start:.1f}s")
                            
                            st.dataframe(
                                df.head(100),
                                use_container_width=True,
                                height=500
                            )
                            
                            # Downloads
                            st.subheader("📥 Export")
                            c1, c2 = st.columns(2)
                            with c1:
                                st.download_button(
                                    "Download CSV",
                                    data=open(output_path, 'rb').read(),
                                    file_name=f"redrob_ranking_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                    mime="text/csv"
                                )
                            with c2:
                                json_str = df.to_json(orient="records", indent=2)
                                st.download_button(
                                    "Download JSON",
                                    data=json_str,
                                    file_name=f"redrob_ranking_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                                    mime="application/json"
                                )
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    # Cleanup
                    for p in [temp_input.name if 'temp_input' in locals() else None, 
                             output_path if 'output_path' in locals() else None]:
                        if p and os.path.exists(p):
                            try:
                                os.unlink(p)
                            except:
                                pass
else:
    st.info("👆 Upload your candidates.jsonl file to begin ranking.")

st.divider()
st.caption("Redrob AI • Production Candidate Intelligence Platform • 2026")
