import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Candidate Ranking System", layout="wide")
st.title("🎯 Candidate Ranking System")

st.sidebar.header("How to use")
st.sidebar.write("""
1. Upload your candidates data (CSV)
2. Define scoring criteria and weights
3. View ranked candidates
""")

# Upload data file
uploaded_file = st.file_uploader("Upload Candidates File", type=["csv", "jsonl", "json"])

if uploaded_file is not None:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    with st.spinner("Loading large file... (this may take a moment)"):
        try:
            if file_ext == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_ext in ['jsonl', 'json']:
                # For large JSONL, read in chunks or sample if too big
                if uploaded_file.size > 100 * 1024 * 1024:  # >100MB
                    st.warning("Large file detected. Loading first 50,000 records for preview and ranking.")
                    df = pd.read_json(uploaded_file, lines=True, nrows=50000)
                else:
                    df = pd.read_json(uploaded_file, lines=True)
            else:
                st.error("Unsupported file type")
                st.stop()
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()
    
    st.subheader(f"Loaded Data Preview ({len(df):,} records)")
    st.dataframe(df.head(20), use_container_width=True)
    
    # Assume columns like Name, Score1, Score2 etc., or allow selection
    st.subheader("Select Scoring Columns")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    
    # Optional: Column filters for large datasets
    if len(df) > 10000:
        st.info("Large dataset – you can filter before ranking.")
        filter_col = st.selectbox("Filter by column (optional)", ["None"] + list(df.columns))
        if filter_col != "None":
            unique_vals = df[filter_col].dropna().unique()
            selected_vals = st.multiselect("Select values", unique_vals[:100])  # limit for UI
            if selected_vals:
                df = df[df[filter_col].isin(selected_vals)]
    
    if not numeric_cols:
        st.error("No numeric columns found for scoring!")
    else:
        criteria = {}
        total_weight = 0
        
        for col in numeric_cols:
            col_weight = st.slider(f"Weight for {col} (%)", 0, 100, 50, key=col)
            criteria[col] = col_weight / 100.0
            total_weight += col_weight
        
        if total_weight != 100:
            st.warning(f"Total weights sum to {total_weight}%. Consider adjusting.")
        
        # Calculate weighted score
        if st.button("Calculate Rankings"):
            with st.spinner("Calculating scores and ranking..."):
                df = df.copy()
                df['Weighted Score'] = 0.0
                for col, weight in criteria.items():
                    # Robust normalization (handle outliers with quantiles optionally)
                    min_val = df[col].quantile(0.01)
                    max_val = df[col].quantile(0.99)
                    if max_val > min_val:
                        norm = (df[col] - min_val) / (max_val - min_val)
                        norm = norm.clip(0, 1)
                    else:
                        norm = 0
                    df['Weighted Score'] += norm * weight
                
                # Rank
                df = df.sort_values('Weighted Score', ascending=False).reset_index(drop=True)
                df['Rank'] = range(1, len(df) + 1)
            
            st.subheader(f"Ranked Candidates (showing top 1,000 of {len(df):,})")
            display_df = df.head(1000)
            st.dataframe(display_df, use_container_width=True)
            
            # Download (full results may be large)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Full Ranked Data (CSV)", csv, "ranked_candidates.csv", "text/csv")
            
            # Visual
            name_col = next((col for col in ['Name', 'name', 'candidate'] if col in df.columns), df.columns[0])
            st.bar_chart(display_df.head(20).set_index(name_col)['Weighted Score'])

else:
    st.info("""Upload your **candidates.jsonl** (or CSV) file.
    
Large files (like your 467MB one) will be sampled for performance.""")

# Manual entry example
st.subheader("Or Add Candidates Manually")
if st.checkbox("Enable Manual Mode"):
    num_candidates = st.number_input("Number of Candidates", 1, 20, 5)
    data = []
    for i in range(num_candidates):
        with st.expander(f"Candidate {i+1}"):
            name = st.text_input("Name", f"Candidate {i+1}", key=f"name_{i}")
            exp = st.number_input("Experience (years)", 0, 30, 5, key=f"exp_{i}")
            skill = st.number_input("Skill Score", 0, 100, 80, key=f"skill_{i}")
            inter = st.number_input("Interview Score", 0, 100, 75, key=f"inter_{i}")
            data.append({"Name": name, "Experience": exp, "Skill_Score": skill, "Interview_Score": inter})
    
    if st.button("Rank Manual Data"):
        manual_df = pd.DataFrame(data)
        # Similar ranking logic
        manual_df['Weighted Score'] = 0.4 * (manual_df['Experience'] / 10) + 0.3 * (manual_df['Skill_Score'] / 100) + 0.3 * (manual_df['Interview_Score'] / 100)
        manual_df = manual_df.sort_values('Weighted Score', ascending=False)
        manual_df['Rank'] = range(1, len(manual_df) + 1)
        st.dataframe(manual_df)
