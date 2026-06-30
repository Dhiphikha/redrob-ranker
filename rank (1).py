import sys
import pandas as pd
import json
import time

def simple_rank(input_path, output_path):
    """Simple ranking function for demonstration"""
    try:
        # Read JSONL
        df = pd.read_json(input_path, lines=True, nrows=100000)  # limit for speed
        
        # Dummy scoring if no score column
        if 'score' not in df.columns:
            numeric_cols = df.select_dtypes(include='number').columns
            if len(numeric_cols) > 0:
                df['score'] = df[numeric_cols].mean(axis=1)
            else:
                df['score'] = 0.85  # default
        
        # Add rank and reasoning
        df = df.sort_values('score', ascending=False).reset_index(drop=True)
        df['rank'] = range(1, len(df) + 1)
        df['reasoning'] = "High match on experience and skills"
        
        # Select top columns
        cols = ['rank', 'score'] + [c for c in df.columns if c not in ['rank', 'score', 'reasoning']]
        df = df[cols[:10]]  # limit columns
        
        df.to_csv(output_path, index=False)
        print(f"Ranked {len(df)} candidates successfully")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python rank.py <input> <output>")
        sys.exit(1)
    simple_rank(sys.argv[1], sys.argv[2])
