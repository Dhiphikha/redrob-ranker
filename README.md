# Redrob Candidate Ranking System

## Approach

I used a scoring system that combines:
- **Title Matching (30%)**: Does their job title match?
- **Skills Matching (25%)**: Do they have the right skills?
- **Experience (20%)**: Do they have enough experience?
- **Education (10%)**: Good educational background?
- **Behavioral Signals (15%)**: Are they engaged/responsive?

## How It Works

1. Load all 100,000 candidates
2. Score each one using the above formula
3. Sort by score (highest first)
4. Take top 100
5. Export to CSV

## How to Run

```bash
python rank.py candidates.jsonl submission.csv
```

## Testing

```bash
python rank.py sample_candidates.json test.csv
python validate_submission.py test.csv
```
