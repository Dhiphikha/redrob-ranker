# Redrob Candidate Ranking System

## Approach
Five-component ranking system for Senior AI Engineer role:

1. **Title Match (30%)**: Exact/related titles in career history
   - Matches: "AI Engineer", "ML Engineer", "Senior Engineer"
   
2. **Skills Match (25%)**: Required ML/Python/Deep Learning skills
   - Proficiency level, duration multiplier, endorsement bonus
   
3. **Experience (20%)**: Years aligned with 5-9 year preference
   
4. **Education (10%)**: Institution tier (Tier 1 preferred)
   
5. **Behavioral Signals (15%)**: Recruiter response, search activity, open to work

## Honeypot Detection
Filters impossible profiles:
- >50 expert skills
- Perfect metrics (1.0 rates)
- Impossible career dates
- Unverified with many skills

## How to Run
```bash
python rank.py candidates.jsonl submission.csv
python validate_submission.py submission.csv
```

## Results
- Runtime: ~12 seconds for 100,000 candidates
- Top 100 candidates ranked by fit
- Honeypot rate: 0.0% (safe)
