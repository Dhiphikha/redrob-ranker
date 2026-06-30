
# Redrob Candidate Ranking System

## Overview
Intelligent ranking system for Senior AI Engineer role at Redrob AI.

## Approach
Five-component scoring system:
1. Title Match (30%)
2. Skills Match (25%)
3. Experience Years (20%)
4. Education Tier (10%)
5. Behavioral Signals (15%)

## How It Works
- Loads 100,000 candidates
- Scores each on 5 dimensions
- Detects honeypots (impossible profiles)
- Sorts by score (descending), candidate_id (ascending)
- Exports top 100 to CSV

## Honeypot Detection
Filters candidates with:
- >50 expert skills
- Perfect metrics (1.0 rates)
- Impossible career dates
- Unverified with red flags

## Usage
```bash
python rank.py candidates.jsonl submission.csv
python validate_submission.py submission.csv
```

## Results
- Runtime: ~12 seconds for 100K candidates
- Honeypot rate: 0.0% (verified)
- Output: submission.csv with 100 ranked candidates

## Files
- `rank.py` - Main ranking engine
- `submission.csv` - Top 100 candidates
- `submission_metadata.yaml` - Submission details
