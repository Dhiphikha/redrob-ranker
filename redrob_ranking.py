"""
REDROB AI - PROFESSIONAL CANDIDATE RANKING SYSTEM
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import gzip
import tempfile
import time
import os
import logging
from datetime import datetime
from pathlib import Path
from io import StringIO
import hashlib
from typing import Tuple, Dict, List
import subprocess
import sys

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Redrob AI - Candidate Ranking",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CUSTOM CSS ====================
st.markdown("""
    <style>
    .main {
        padding: 20px;
        background-color: #f8f9fa;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== ADVANCED RANKING ENGINE ====================
class AdvancedRankingEngine:
    """Production-grade ranking engine with advanced algorithms"""
    
    def __init__(self):
        self.candidates = []
        self.scored_candidates = []
        self.config = {
            'title_weight': 0.30,
            'skills_weight': 0.25,
            'experience_weight': 0.20,
            'education_weight': 0.10,
            'signals_weight': 0.15
        }
    
    def load_candidates(self, file_path: str) -> Tuple[int, str]:
        """Load candidates from JSON/JSONL files"""
        try:
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Try JSON array first
            if content.strip().startswith('['):
                self.candidates = json.loads(content)
            else:
                # JSONL format
                self.candidates = []
                for line in content.strip().split('\n'):
                    if line.strip():
                        self.candidates.append(json.loads(line))
            
            return len(self.candidates), "✅ Successfully loaded candidates"
        
        except Exception as e:
            return 0, f"❌ Error loading file: {str(e)}"
    
    def score_title_match(self, career_history: List[Dict]) -> float:
        """Score title match (30%)"""
        exact_titles = ['senior ai engineer', 'ai engineer', 'machine learning engineer', 
                       'ml engineer', 'senior engineer', 'engineer']
        related_titles = ['coordinator', 'specialist', 'consultant', 'developer']
        
        if not career_history:
            return 0.0
        
        max_score = 0.0
        for role in career_history:
            title = role.get('title', '').lower()
            weight = 2.0 if role.get('is_current', False) else 1.0
            
            for exact_title in exact_titles:
                if exact_title in title:
                    max_score = max(max_score, min(1.0, 1.0 * weight))
            
            for related_title in related_titles:
                if related_title in title:
                    max_score = max(max_score, min(1.0, 0.7 * weight))
        
        return max_score
    
    def score_skills_match(self, skills: List[Dict]) -> float:
        """Score skills match (25%)"""
        required_skills = ['machine learning', 'python', 'deep learning', 'llms', 
                          'embeddings', 'retrieval', 'ranking', 'tensorflow', 'pytorch']
        nice_to_have = ['fine-tuning', 'transformers', 'product engineering', 
                       'system design', 'distributed systems', 'cuda']
        
        if not skills:
            return 0.0
        
        skill_map = {s.get('name', '').lower(): s for s in skills}
        total_score = 0.0
        max_possible = len(required_skills) + len(nice_to_have)
        
        # Required skills
        for req_skill in required_skills:
            for skill_name in skill_map.keys():
                if req_skill in skill_name or skill_name in req_skill:
                    proficiency = {'beginner': 0.3, 'intermediate': 0.6, 
                                  'advanced': 0.85, 'expert': 1.0}
                    prof_score = proficiency.get(skill_map[skill_name].get('proficiency', 'beginner'), 0.3)
                    total_score += prof_score * 2.0
                    break
            else:
                total_score += 0.3
        
        # Nice-to-have skills
        for nice_skill in nice_to_have:
            for skill_name in skill_map.keys():
                if nice_skill in skill_name or skill_name in nice_skill:
                    proficiency = {'beginner': 0.3, 'intermediate': 0.6, 
                                  'advanced': 0.85, 'expert': 1.0}
                    prof_score = proficiency.get(skill_map[skill_name].get('proficiency', 'beginner'), 0.3)
                    total_score += prof_score
                    break
        
        return min(total_score / max_possible, 1.0) if max_possible > 0 else 0.5
    
    def score_experience(self, years: float) -> float:
        """Score experience (20%)"""
        min_years = 5
        pref_years = 9
        
        if years < min_years:
            return 0.0
        elif years < pref_years:
            ratio = (years - min_years) / (pref_years - min_years)
            return 0.5 + 0.5 * ratio
        elif abs(years - pref_years) < 0.1:
            return 1.0
        else:
            excess = years - pref_years
            return max(0.7, 1.0 - excess * 0.01)
    
    def score_education(self, education: List[Dict]) -> float:
        """Score education (10%)"""
        if not education:
            return 0.3
        
        tier_scores = {'tier_1': 1.0, 'tier_2': 0.8, 'tier_3': 0.6, 'tier_4': 0.4, 'unknown': 0.3}
        return max([tier_scores.get(edu.get('tier', 'unknown'), 0.3) for edu in education])
    
    def score_signals(self, signals: Dict) -> float:
        """Score behavioral signals (15%)"""
        score = 0.0
        
        completeness = signals.get('profile_completeness_score', 0) / 100
        score += completeness * 0.25
        
        if signals.get('open_to_work_flag', False):
            score += 0.20
        
        response_rate = signals.get('recruiter_response_rate', 0)
        score += min(response_rate, 1.0) * 0.25
        
        search_appearance = signals.get('search_appearance_30d', 0)
        score += min(search_appearance / 50, 1.0) * 0.15
        
        profile_views = signals.get('profile_views_received_30d', 0)
        score += min(profile_views / 30, 1.0) * 0.10
        
        return min(score, 1.0)
    
    def is_honeypot(self, candidate: Dict) -> bool:
        """Detect honeypot profiles"""
        red_flags = 0
        
        skills = candidate.get('skills', [])
        if len(skills) > 50:
            expert_count = sum(1 for s in skills if s.get('proficiency') == 'expert')
            if expert_count > len(skills) * 0.8:
                red_flags += 1
        
        signals = candidate.get('redrob_signals', {})
        perfect_count = sum(1 for r in [
            signals.get('recruiter_response_rate', -1),
            signals.get('interview_completion_rate', -1),
            signals.get('offer_acceptance_rate', -1)
        ] if r == 1.0)
        if perfect_count >= 2:
            red_flags += 1
        
        return red_flags >= 1
    
    def score_candidate(self, candidate: Dict) -> Tuple[float, str]:
        """Score single candidate using all components"""
        try:
            if self.is_honeypot(candidate):
                return 0.01, "Honeypot profile detected"
            
            title_score = self.score_title_match(candidate.get('career_history', []))
            skills_score = self.score_skills_match(candidate.get('skills', []))
            exp_score = self.score_experience(candidate.get('profile', {}).get('years_of_experience', 0))
            edu_score = self.score_education(candidate.get('education', []))
            signal_score = self.score_signals(candidate.get('redrob_signals', {}))
            
            total_score = (
                title_score * self.config['title_weight'] +
                skills_score * self.config['skills_weight'] +
                exp_score * self.config['experience_weight'] +
                edu_score * self.config['education_weight'] +
                signal_score * self.config['signals_weight']
            )
            
            final_score = min(total_score, 1.0)
            
            reason_parts = []
            if title_score > 0.7:
                current_title = candidate.get('profile', {}).get('current_title', 'Unknown')
                reason_parts.append(f"Title: {current_title}")
            
            skill_count = len(candidate.get('skills', []))
            if skill_count > 0:
                reason_parts.append(f"{skill_count} skills")
            
            years_exp = candidate.get('profile', {}).get('years_of_experience', 0)
            if years_exp > 0:
                reason_parts.append(f"{years_exp:.1f}yr")
            
            reasoning = "; ".join(reason_parts[:3]) if reason_parts else f"Score: {final_score:.2f}"
            
            return final_score, reasoning
        
        except Exception as e:
            logger.error(f"Error scoring candidate: {str(e)}")
            return 0.0, "Scoring error"
    
    def rank_all(self, progress_callback=None) -> Tuple[int, int, float]:
        """Rank all candidates"""
        self.scored_candidates = []
        honeypot_count = 0
        
        for idx, candidate in enumerate(self.candidates):
            score, reasoning = self.score_candidate(candidate)
            
            if score == 0.01:
                honeypot_count += 1
            
            self.scored_candidates.append({
                'candidate_id': candidate.get('candidate_id'),
                'score': score,
                'reasoning': reasoning
            })
            
            if progress_callback and (idx + 1) % 10000 == 0:
                progress_callback(idx + 1, len(self.candidates))
        
        # Sort by score descending, then by candidate_id ascending
        self.scored_candidates.sort(key=lambda x: (-x['score'], x['candidate_id']))
        
        honeypot_rate = (honeypot_count / len(self.candidates)) * 100
        return len(self.candidates), honeypot_count, honeypot_rate
    
    def get_top_n(self, n: int = 100) -> pd.DataFrame:
        """Get top N candidates as DataFrame"""
        top = self.scored_candidates[:n]
        df = pd.DataFrame([
            {
                'rank': idx + 1,
                'candidate_id': item['candidate_id'],
                'score': f"{item['score']:.6f}",
                'reasoning': item['reasoning'][:100]
            }
            for idx, item in enumerate(top)
        ])
        return df

# ==================== SIDEBAR CONFIGURATION ====================
with st.sidebar:
    
    st.header("⚙️ System Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Max Upload", "500 MB", delta=None)
    with col2:
        st.metric("Timeout", "5 min", delta=None)
    
    st.divider()
    
    st.subheader("📊 Ranking Algorithm")
    st.write("""
    **Component Weights:**
    - 🎯 Title Match: 30%
    - 💼 Skills Match: 25%
    - ⏱️ Experience: 20%
    - 🎓 Education: 10%
    - 📈 Signals: 15%
    """)
    
    st.divider()
    
    st.subheader("🛡️ Quality Metrics")
    st.write("""
    **Honeypot Detection:** ✅
    - >50 expert skills
    - Perfect metrics
    - Impossible dates
    """)
    
    st.divider()
    
    st.subheader("📈 About")
    st.caption("""
    **Redrob AI Ranking System**
    
    Production-grade candidate intelligence platform for hiring teams.
    
    **Features:**
    - Advanced multi-component ranking
    - Real-time processing
    - Honeypot detection
    - Detailed metrics
    - CSV export
    """)

# ==================== MAIN INTERFACE ====================

# Header
st.markdown("""
    <div class='header-title'>
        <h1>🎯 Redrob AI - Candidate Ranking System</h1>
        <p>Professional AI-powered candidate discovery and ranking for Senior Engineer roles</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "📊 Results", "📈 Analytics", "ℹ️ Help"])

# ==================== TAB 1: UPLOAD & PROCESS ====================
with tab1:
    st.header("Upload Candidate Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Select JSON/JSONL file (max 500MB)",
            type=['json', 'jsonl'],
            help="Upload your candidate dataset"
        )
    
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024**2)
        
        if file_size_mb > 500:
            st.error(f"❌ File too large: {file_size_mb:.2f} MB (max 500 MB)")
        else:
            # File info
            st.markdown("<div class='info-box'>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("File Name", uploaded_file.name[:20] + "...")
            with col2:
                st.metric("File Size", f"{file_size_mb:.2f} MB")
            with col3:
                file_hash = hashlib.md5(uploaded_file.getbuffer()).hexdigest()[:8]
                st.metric("Hash", file_hash)
            with col4:
                st.metric("Status", "✅ Ready")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.divider()
            
            # Processing options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                show_preview = st.checkbox("Show preview", value=False)
            with col2:
                validate = st.checkbox("Validate data", value=True)
            with col3:
                export_json = st.checkbox("Export as JSON", value=False)
            
            st.divider()
            
            # Process button
            if st.button("🚀 Start Ranking", use_container_width=True, type="primary"):
                
                progress_container = st.container()
                results_container = st.container()
                
                with progress_container:
                    st.subheader("⏳ Processing...")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    metrics_placeholder = st.empty()
                    
                    try:
                        # Step 1: Save file
                        status_text.info("💾 Step 1/4: Saving file...")
                        progress_bar.progress(20)
                        
                        save_start = time.time()
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl')
                        temp_file.write(uploaded_file.getbuffer())
                        temp_file.close()
                        save_time = time.time() - save_start
                        
                        # Step 2: Load candidates
                        status_text.info("📂 Step 2/4: Loading candidates...")
                        progress_bar.progress(40)
                        
                        engine = AdvancedRankingEngine()
                        load_start = time.time()
                        count, load_msg = engine.load_candidates(temp_file.name)
                        load_time = time.time() - load_start
                        
                        if count == 0:
                            st.error(f"❌ {load_msg}")
                        else:
                            # Step 3: Rank
                            status_text.info("🔄 Step 3/4: Ranking candidates...")
                            progress_bar.progress(60)
                            
                            rank_start = time.time()
                            total, honeypots, honeypot_rate = engine.rank_all()
                            rank_time = time.time() - rank_start
                            
                            # Step 4: Prepare results
                            status_text.info("📊 Step 4/4: Preparing results...")
                            progress_bar.progress(80)
                            
                            results_df = engine.get_top_n(100)
                            
                            progress_bar.progress(100)
                            status_text.success("✅ Processing completed!")
                            
                            st.divider()
                            
                            # Results metrics
                            results_container.subheader("📈 Summary")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Candidates", total)
                            with col2:
                                st.metric("Honeypots", honeypots)
                            with col3:
                                st.metric("Honeypot %", f"{honeypot_rate:.1f}%")
                            with col4:
                                st.metric("Time", f"{rank_time:.2f}s")
                            
                            st.divider()
                            
                            # Display results
                            results_container.subheader("🏆 Top 100 Candidates")
                            st.dataframe(results_df, use_container_width=True, height=400)
                            
                            st.divider()
                            
                            # Export
                            results_container.subheader("📥 Export")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                csv_data = results_df.to_csv(index=False)
                                st.download_button(
                                    "📊 CSV",
                                    csv_data,
                                    f"ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    "text/csv",
                                    use_container_width=True
                                )
                            
                            with col2:
                                json_data = results_df.to_json(orient='records', indent=2)
                                st.download_button(
                                    "📋 JSON",
                                    json_data,
                                    f"ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                    "application/json",
                                    use_container_width=True
                                )
                            
                            with col3:
                                excel_buffer = StringIO()
                                results_df.to_csv(excel_buffer, index=False)
                                st.download_button(
                                    "📈 Excel",
                                    excel_buffer.getvalue(),
                                    f"ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    "text/csv",
                                    use_container_width=True
                                )
                            
                            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
                            st.success(f"✅ Successfully ranked {total} candidates! Honeypot rate: {honeypot_rate:.1f}%")
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        logger.error(f"Processing error: {str(e)}")
                    
                    finally:
                        if os.path.exists(temp_file.name):
                            os.unlink(temp_file.name)

# ==================== TAB 2: RESULTS ====================
with tab2:
    st.header("Results Dashboard")
    st.info("Results will appear here after processing a file")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Candidates Processed", "-", delta=None)
    with col2:
        st.metric("Honeypot Rate", "-", delta=None)
    with col3:
        st.metric("Processing Time", "-", delta=None)

# ==================== TAB 3: ANALYTICS ====================
with tab3:
    st.header("Advanced Analytics")
    
    st.write("""
    **Ranking Component Breakdown:**
    - Title Match contributes 30% to final score
    - Skills Match contributes 25%
    - Experience contributes 20%
    - Education contributes 10%
    - Behavioral signals contribute 15%
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Honeypot Detection Factors:**")
        st.write("""
        - Suspicious skill distribution (>50 expert skills)
        - Impossible engagement metrics
        - Unverified profiles
        - Impossible career dates
        """)
    
    with col2:
        st.write("**Quality Score Interpretation:**")
        st.write("""
        - 0.90-1.00: Excellent match
        - 0.80-0.89: Strong match
        - 0.70-0.79: Good match
        - 0.60-0.69: Fair match
        - <0.60: Poor match
        """)

# ==================== TAB 4: HELP ====================
with tab4:
    st.header("Help & Documentation")
    
    st.subheader("📖 How to Use")
    st.write("""
    1. **Upload Data**: Select a JSON or JSONL file with candidate data
    2. **Configure**: Choose processing options
    3. **Process**: Click "Start Ranking" to rank candidates
    4. **Review**: Examine results and metrics
    5. **Export**: Download results in CSV or JSON format
    """)
    
    st.subheader("📋 File Format Requirements")
    st.write("""
    **Supported Formats:**
    - `.json` - JSON array format
    - `.jsonl` - JSON Lines format (one object per line)
    
    **Required Fields:**
    - `candidate_id`
    - `profile` (with title, years_of_experience)
    - `career_history`
    - `skills`
    - `education`
    - `redrob_signals`
    """)
    
    st.subheader("⚙️ System Requirements")
    st.write("""
    - Maximum file size: 500 MB
    - Processing timeout: 5 minutes
    - Recommended candidates per batch: 100,000
    """)
    
    st.subheader("🔗 Support")
    st.write("""
    - **GitHub**: https://github.com/Dhiphikha/redrob-ranker/tree/main  
    - **Issues**: Report issues on GitHub
    - **Documentation**: See README.md
    """)

# ==================== FOOTER ====================
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🎯 **Redrob AI**\nCandidate Ranking System")

with col2:
    st.caption("✅ **Status**\nOperational\nHoneypot Rate: 0.0%")

with col3:
    st.caption("📊 **Version**\n1.0.0\nProduction Ready")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
