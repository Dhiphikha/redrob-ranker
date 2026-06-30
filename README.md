# Redrob Candidate Ranking System

## Approach
Five-component scoring system:
- **Title Match (30%)**: Exact/related job titles in career history
- **Skills Match (25%)**: Required ML/Python skills with proficiency weighting
- **Experience (20%)**: Years aligned with 5-9 year preference
- **Education (10%)**: Institution tier (Tier 1 preferred)
- **Behavioral Signals (15%)**: Recruiter response rate, search appearance

## How It Works
1. Load 100,000 candidates
2. Score each on 5 dimensions
3. Sort by score descending, candidate_id ascending (tie-break)
4. Export top 100 to CSV

## Honeypot Detection
Filters impossible profiles:
- >50 expert skills
- Perfect metrics (1.0 rates)
- Impossible career dates
- Unverified with red flags

## Running It
```bash
python rank.py candidates.jsonl submission.csv
python validate_submission.py submission.csv
```

## Results
- Runtime: ~12 seconds for 100K candidates
- Output: submission.csv with top 100 ranked candidates
