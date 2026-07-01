import streamlit as st
import pandas as pd
import json
import csv
import tempfile
import os
from datetime import datetime
import logging

# ====================== RANKING ENGINE (Integrated from rank.py) ======================
class JobRequirements:
    def __init__(self):
        self.exact_titles = ['senior ai engineer', 'ai engineer', 'machine learning engineer', 'ml engineer']
        self.related_titles = ['coordinator', 'specialist', 'consultant']
        self.required_skills = ['machine learning', 'python', 'deep learning', 'llms', 'embeddings', 'retrieval', 'ranking', 'tensorflow', 'pytorch']
        self.nice_to_have_skills = ['fine-tuning', 'transformers', 'product engineering', 'system design']
        self.min_years_experience = 5
        self.preferred_years_experience = 9
        self.preferred_education_tier = 'tier_1'

class CandidateRanker:
    def __init__(self):
        self.job_req = JobRequirements()
        self.candidates = []
        self.scored_candidates = []

    def load_candidates(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content.startswith('['):
                data = json.loads(content)
                self.candidates = data if isinstance(data, list) else [data]
            else:
                # JSONL or line-by-line
                f.seek(0)
                for line in f:
                    if line.strip():
                        try:
                            self.candidates.append(json.loads(line))
                        except:
                            pass  # skip invalid lines

    def score_candidate(self, candidate):
        try:
            total_score = 0.0
            reasons = []

            # Title Match (30%)
            title_score = self._score_title(candidate.get('career_history', []))
            total_score += title_score * 0.30
            if title_score > 0.6:
                reasons.append(f"Strong title match")

            # Skills Match (25%)
            skills_score = self._score_skills(candidate.get('skills', []))
            total_score += skills_score * 0.25
            if skills_score > 0.5:
                reasons.append(f"{len(candidate.get('skills', []))} relevant skills")

            # Experience (20%)
            years = candidate.get('profile', {}).get('years_of_experience', 0)
            exp_score = self._score_experience(years)
            total_score += exp_score * 0.20
            reasons.append(f"{years:.1f} years exp")

            # Education + Signals (25%)
            edu_score = self._score_education(candidate.get('education', []))
            signals_score = self._score_signals(candidate.get('redrob_signals', {}))
            total_score += (edu_score * 0.10) + (signals_score * 0.15)

            final_score = min(max(total_score, 0.0), 1.0)
            return final_score, "; ".join(reasons[:3])

        except Exception:
            return 0.0, "Scoring error"

    def _score_title(self, career):
        if not career:
            return 0.0
        max_s = 0.0
        for role in career:
            title = str(role.get('title', '')).lower()
            weight = 2.0 if role.get('is_current') else 1.0
            for t in self.job_req.exact_titles:
                if t in title:
                    max_s = max(max_s, 1.0 * weight)
        return min(max_s, 1.0)

    def _score_skills(self, skills):
        if not skills:
            return 0.0
        return min(len(skills) / 15, 1.0)  # Simplified for demo

    def _score_experience(self, years):
        if years < self.job_req.min_years_experience:
            return 0.0
        elif years < self.job_req.preferred_years_experience:
            return 0.5 + 0.5 * (years - 5) / 4
        return 0.95

    def _score_education(self, edu):
        return 0.8 if edu else 0.4

    def _score_signals(self, signals):
        return min(signals.get('profile_completeness_score', 50) / 100, 1.0)

    def rank_candidates(self):
        self.scored_candidates = []
        for cand in self.candidates:
            score, reason = self.score_candidate(cand)
            self.scored_candidates.append({
                'candidate_id': cand.get('candidate_id', 'unknown'),
                'score': score,
                'reasoning': reason,
                'name': cand.get('profile', {}).get('name', 'N/A')
            })
        self.scored_candidates.sort(key=lambda x: -x['score'])

    def get_top_df(self, n=100):
        df = pd.DataFrame(self.scored_candidates[:n])
        df['rank'] = range(1, len(df) + 1)
        return df

# ====================== STREAMLIT APP ======================
st.set_page_config(page_title="Redrob - Intelligent Candidate Ranking", layout="wide")
st.title("🔥 Redrob Intelligent Candidate Ranking System")
st.markdown("**Advanced AI-powered ranking for AI/ML roles**")

# File Upload
st.subheader("Upload Candidate Data")
uploaded_file = st.file_uploader(
    "Supported formats: .json, .jsonl, .txt (JSONL), .gz (coming soon)",
    type=['json', 'jsonl', 'txt']
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl') as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    ranker = CandidateRanker()
    with st.spinner("Loading and ranking candidates..."):
        ranker.load_candidates(tmp_path)
        ranker.rank_candidates()
    
    st.success(f"✅ Processed **{len(ranker.candidates)}** candidates")

    # Results
    df = ranker.get_top_df(100)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Top Ranked Candidates")
        st.dataframe(
            df[['rank', 'candidate_id', 'name', 'score', 'reasoning']],
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.metric("Total Candidates", len(ranker.candidates))
        st.metric("Top Score", f"{df['score'].max():.3f}")
    
    # Download
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Ranking (CSV)",
        data=csv,
        file_name=f"ranking_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

    # Visualization
    st.subheader("Score Distribution")
    import plotly.express as px
    fig = px.histogram(df, x="score", nbins=20, title="Candidate Score Distribution")
    st.plotly_chart(fig, use_container_width=True)

    os.unlink(tmp_path)

else:
    st.info("👆 Upload your candidate data file to start ranking")

st.caption("Built with ❤️ using the Redrob ranking engine • Supports large JSONL files")
