#!/usr/bin/env python3
"""
Redrob Hackathon: Intelligent Candidate Ranking System
Complete implementation template ready for customization
"""

import gzip
import json
import csv
import sys
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JobRequirements:
    def __init__(self):
        # Exact title matches (highest priority)
        self.exact_titles = [
            'senior ai engineer',
            'ai engineer',
            'machine learning engineer',
            'ml engineer',
            'senior engineer',
            'engineer',
        ]

        # Related titles (medium priority)
        self.related_titles = [
            'coordinator',
            'specialist',
            'consultant',
        ]
        
        self.required_skills = [
            'machine learning',
            'python',
            'deep learning',
            'llms',
            'embeddings',
            'retrieval',
            'ranking',
            'tensorflow',
            'pytorch',
        ]
        
        self.nice_to_have_skills = [
            'fine-tuning',
            'transformers',
            'product engineering',
            'system design',
            'distributed systems',
            'cuda',
        ]
        
        # Experience requirements
        self.min_years_experience = 5
        self.preferred_years_experience = 9
        
        # Education preference
        self.preferred_education_tier = 'tier_1'  # tier_1, tier_2, tier_3, tier_4, unknown
        
        # Location/relocation
        self.require_relocation = False
        self.preferred_locations = ['India', 'Remote']
        
        # Work mode
        self.preferred_work_modes = ['remote', 'hybrid']
        
        # Tech role?
        self.is_tech_role = True
        
        # =====================================================================


class CandidateRanker:
    """Main ranking engine"""
    
    def __init__(self):
        self.job_req = JobRequirements()
        self.candidates: List[Dict] = []
        self.scored_candidates: List[Dict] = []
        
    def load_candidates(self, input_file: str) -> None:
        """Load candidates from JSON/JSONL or gzipped versions"""
        logger.info(f"Loading candidates from {input_file}...")
        
        try:
            if input_file.endswith('.gz'):
                with gzip.open(input_file, 'rt', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if line.strip():
                            try:
                                candidate = json.loads(line)
                                self.candidates.append(candidate)
                            except json.JSONDecodeError as e:
                                logger.warning(f"Line {line_num}: Invalid JSON - {e}")
                        
                        if line_num % 20000 == 0:
                            logger.info(f"  Loaded {line_num} candidates...")
            else:
                with open(input_file, 'r', encoding='utf-8') as f:
                    # Check if single JSON array or JSONL
                    content = f.read()
                    
                    if content.strip().startswith('['):
                        # JSON array format
                        data = json.loads(content)
                        self.candidates = data if isinstance(data, list) else [data]
                    else:
                        # JSONL format
                        f.seek(0)
                        for line_num, line in enumerate(f, 1):
                            if line.strip():
                                try:
                                    candidate = json.loads(line)
                                    self.candidates.append(candidate)
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Line {line_num}: Invalid JSON - {e}")
        
        except FileNotFoundError:
            logger.error(f"File not found: {input_file}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error loading candidates: {e}")
            sys.exit(1)
        
        logger.info(f"✓ Successfully loaded {len(self.candidates)} candidates")
    
    def score_candidate(self, candidate: Dict) -> Tuple[float, str]:
        """
        Score a single candidate across multiple dimensions
        Returns: (score 0-1.0, reasoning string)
        """
        
        try:
            # Early exit: honeypot detection
            if self._is_honeypot(candidate):
                return 0.01, "Honeypot profile detected"
            
            total_score = 0.0
            reason_parts = []
            
            # ===== COMPONENT 1: TITLE MATCH (30% weight) =====
            title_score = self._score_title_match(candidate.get('career_history', []))
            total_score += title_score * 0.30
            if title_score > 0.7:
                current_title = candidate.get('profile', {}).get('current_title', 'Unknown')
                reason_parts.append(f"Title: {current_title}")
            
            # ===== COMPONENT 2: SKILLS MATCH (25% weight) =====
            skills_score = self._score_skills_match(candidate.get('skills', []))
            total_score += skills_score * 0.25
            skills = candidate.get('skills', [])
            skill_count = len(skills)
            if skill_count > 0:
                reason_parts.append(f"{skill_count} skills")
            
            # ===== COMPONENT 3: EXPERIENCE (20% weight) =====
            years_exp = candidate.get('profile', {}).get('years_of_experience', 0)
            exp_score = self._score_experience(years_exp)
            total_score += exp_score * 0.20
            if years_exp > 0:
                reason_parts.append(f"{years_exp:.1f}yr")
            
            # ===== COMPONENT 4: EDUCATION (10% weight) =====
            edu_score = self._score_education(candidate.get('education', []))
            total_score += edu_score * 0.10
            
            # ===== COMPONENT 5: BEHAVIORAL SIGNALS (15% weight) =====
            signals_score = self._score_signals(candidate.get('redrob_signals', {}))
            total_score += signals_score * 0.15
            response_rate = candidate.get('redrob_signals', {}).get('recruiter_response_rate', 0)
            if response_rate > 0:
                reason_parts.append(f"response:{response_rate:.1%}")
            
            # Cap score at 1.0
            final_score = min(total_score, 1.0)
            
            # Build reasoning (1-2 short sentences)
            reasoning = "; ".join(reason_parts[:3])
            if not reasoning:
                reasoning = f"Score: {final_score:.2f}"
            
            return final_score, reasoning
        
        except Exception as e:
            logger.warning(f"Error scoring candidate {candidate.get('candidate_id')}: {e}")
            return 0.0, "Scoring error"
    
    def _score_title_match(self, career_history: List[Dict]) -> float:
        """
        Score based on job title match
        Exact match = 1.0, Related = 0.7, Similar = 0.4
        Current role weighted 2x
        """
        if not career_history:
            return 0.0
        
        max_score = 0.0
        
        for role in career_history:
            title = role.get('title', '').lower()
            if not title:
                continue
            
            # Weight current roles higher
            weight = 2.0 if role.get('is_current', False) else 1.0
            
            # Check exact matches
            for exact_title in self.job_req.exact_titles:
                if exact_title.lower() in title:
                    max_score = max(max_score, min(1.0, 1.0 * weight))
            
            # Check related matches
            for related_title in self.job_req.related_titles:
                if related_title.lower() in title:
                    max_score = max(max_score, min(1.0, 0.7 * weight))
        
        return max_score
    
    def _score_skills_match(self, skills: List[Dict]) -> float:
        """
        Score based on required vs actual skills
        Considers: proficiency level, endorsements, duration of use
        """
        if not skills:
            return 0.0
        
        # Build skill lookup
        skill_map = {s.get('name', '').lower(): s for s in skills}
        
        total_score = 0.0
        max_possible = len(self.job_req.required_skills) + len(self.job_req.nice_to_have_skills)
        
        if max_possible == 0:
            return 0.5
        
        # Score required skills (weight = 2.0)
        for req_skill in self.job_req.required_skills:
            req_skill_lower = req_skill.lower()
            
            # Fuzzy matching
            matched = False
            for skill_name, skill_obj in skill_map.items():
                if req_skill_lower in skill_name or skill_name in req_skill_lower:
                    # Proficiency score
                    proficiency_map = {
                        'beginner': 0.3,
                        'intermediate': 0.6,
                        'advanced': 0.85,
                        'expert': 1.0
                    }
                    prof_score = proficiency_map.get(skill_obj.get('proficiency', 'beginner'), 0.3)
                    
                    # Duration multiplier
                    duration_months = skill_obj.get('duration_months', 0)
                    if duration_months >= 12:
                        duration_mult = 1.5
                    elif duration_months >= 6:
                        duration_mult = 1.2
                    else:
                        duration_mult = 1.0
                    
                    # Endorsement bonus
                    endorsements = skill_obj.get('endorsements', 0)
                    endorsement_bonus = min(0.2, endorsements / 50)
                    
                    skill_score = (prof_score * duration_mult + endorsement_bonus) * 2.0
                    total_score += min(skill_score, 2.0)
                    matched = True
                    break
            
            if not matched:
                # Slight penalty for missing required skill
                total_score += 0.3
        
        # Score nice-to-have skills (weight = 1.0)
        for nice_skill in self.job_req.nice_to_have_skills:
            nice_skill_lower = nice_skill.lower()
            
            for skill_name, skill_obj in skill_map.items():
                if nice_skill_lower in skill_name or skill_name in nice_skill_lower:
                    proficiency_map = {
                        'beginner': 0.3,
                        'intermediate': 0.6,
                        'advanced': 0.85,
                        'expert': 1.0
                    }
                    prof_score = proficiency_map.get(skill_obj.get('proficiency', 'beginner'), 0.3)
                    total_score += prof_score
                    break
        
        return min(total_score / max_possible, 1.0) if max_possible > 0 else 0.5
    
    def _score_experience(self, years: float) -> float:
        """
        Score based on years of experience
        < min = 0.0
        min = 0.5
        preferred = 1.0
        > preferred = 0.9 (slight over-qualification penalty)
        """
        min_yrs = self.job_req.min_years_experience
        pref_yrs = self.job_req.preferred_years_experience
        
        if years < min_yrs:
            return 0.0
        elif years < pref_yrs:
            ratio = (years - min_yrs) / (pref_yrs - min_yrs)
            return 0.5 + 0.5 * ratio
        elif abs(years - pref_yrs) < 0.1:  # Essentially equal
            return 1.0
        else:
            # Over-qualification slight penalty
            excess = years - pref_yrs
            return max(0.7, 1.0 - excess * 0.01)
    
    def _score_education(self, education: List[Dict]) -> float:
        """
        Score based on institution tier
        tier_1 = 1.0, tier_2 = 0.8, tier_3 = 0.6, tier_4 = 0.4, unknown = 0.3
        Takes best education
        """
        if not education:
            return 0.3  # Some credit for experience over education
        
        tier_scores = {
            'tier_1': 1.0,
            'tier_2': 0.8,
            'tier_3': 0.6,
            'tier_4': 0.4,
            'unknown': 0.3
        }
        
        best_score = 0.0
        for edu_item in education:
            tier = edu_item.get('tier', 'unknown')
            score = tier_scores.get(tier, 0.3)
            best_score = max(best_score, score)
        
        return best_score
    
    def _score_signals(self, signals: Dict) -> float:
        """
        Score based on Redrob behavioral signals
        - Profile completeness (0-100)
        - Open to work flag
        - Recruiter response rate
        - Recent search appearance
        - Recent activity
        """
        score = 0.0
        
        # Profile completeness (0-0.25)
        completeness = signals.get('profile_completeness_score', 0) / 100
        score += completeness * 0.25
        
        # Open to work flag (0-0.20)
        if signals.get('open_to_work_flag', False):
            score += 0.20
        
        # Recruiter response rate (0-0.25)
        response_rate = signals.get('recruiter_response_rate', 0)
        score += min(response_rate, 1.0) * 0.25
        
        # Search appearance in last 30 days (0-0.15)
        search_appearance = signals.get('search_appearance_30d', 0)
        score += min(search_appearance / 50, 1.0) * 0.15
        
        # Recent profile views (0-0.10)
        profile_views = signals.get('profile_views_received_30d', 0)
        score += min(profile_views / 30, 1.0) * 0.10
        
        # Location/relocation match (optional bonus)
        if self.job_req.require_relocation:
            if signals.get('willing_to_relocate', False):
                score += 0.05
        
        return min(score, 1.0)
    
    def _is_honeypot(self, candidate: Dict) -> bool:
        """
        Detect impossible/trap candidates
        Red flags:
        - Too many expert skills (>50 skills, >80% expert)
        - Perfect metrics (response=1.0, interview=1.0, offer=1.0)
        - Unverified with suspicious profile
        - Impossible dates
        """
        red_flags = 0
        
        # Flag 1: Absurd skill count and proficiency
        skills = candidate.get('skills', [])
        if len(skills) > 50:
            expert_count = sum(1 for s in skills if s.get('proficiency') == 'expert')
            if expert_count > len(skills) * 0.8:
                red_flags += 1
        
        # Flag 2: Perfect engagement metrics
        signals = candidate.get('redrob_signals', {})
        response_rate = signals.get('recruiter_response_rate', -1)
        interview_rate = signals.get('interview_completion_rate', -1)
        offer_rate = signals.get('offer_acceptance_rate', -1)
        
        perfect_count = sum(1 for r in [response_rate, interview_rate, offer_rate] if r == 1.0)
        if perfect_count >= 2:
            red_flags += 1
        
        # Flag 3: Unverified profile with many skills
        verified_email = signals.get('verified_email', False)
        verified_phone = signals.get('verified_phone', False)
        if not verified_email and not verified_phone and len(skills) > 25:
            red_flags += 1
        
        # Flag 4: Check for impossible dates in career history
        career = candidate.get('career_history', [])
        for role in career:
            start_str = role.get('start_date')
            end_str = role.get('end_date')
            
            if start_str and end_str:
                try:
                    start = datetime.strptime(start_str, '%Y-%m-%d')
                    end = datetime.strptime(end_str, '%Y-%m-%d')
                    if end < start:
                        red_flags += 1
                except:
                    pass
        
        # Threshold: 1+ major red flag = honeypot
        return red_flags >= 1
    
    def rank_all_candidates(self) -> None:
        """Score and rank all candidates"""
        logger.info("Scoring all candidates...")
        
        self.scored_candidates = []
        
        for idx, candidate in enumerate(self.candidates):
            score, reasoning = self.score_candidate(candidate)
            
            self.scored_candidates.append({
                'candidate_id': candidate.get('candidate_id'),
                'score': score,
                'reasoning': reasoning,
            })
            
            if (idx + 1) % 25000 == 0:
                logger.info(f"  Scored {idx + 1}/{len(self.candidates)}")
        
        logger.info("✓ Scoring complete")
        
        # Sort: primary by score descending, secondary by candidate_id ascending
        logger.info("Sorting candidates...")
        self.scored_candidates.sort(
            key=lambda x: (-x['score'], x['candidate_id'])
        )
        logger.info("✓ Sorting complete")
    
    def export_top_100(self, output_file: str) -> None:
        """Export top 100 candidates to CSV"""
        logger.info(f"Exporting top 100 to {output_file}...")
        
        top_100 = self.scored_candidates[:100]
        
        if len(top_100) < 100:
            logger.warning(f"Only {len(top_100)} candidates available, exporting all")
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['candidate_id', 'rank', 'score', 'reasoning']
                )
                writer.writeheader()
                
                for rank, candidate in enumerate(top_100, 1):
                    # Truncate reasoning to reasonable length
                    reasoning = candidate['reasoning'][:200]
                    
                    writer.writerow({
                        'candidate_id': candidate['candidate_id'],
                        'rank': rank,
                        'score': f"{candidate['score']:.6f}",
                        'reasoning': reasoning
                    })
            
            logger.info(f"✓ Successfully exported {len(top_100)} candidates")
            logger.info(f"✓ Output file: {output_file}")
        
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            sys.exit(1)
    
    def run(self, input_file: str, output_file: str) -> None:
        """Execute full ranking pipeline"""
        logger.info("=" * 60)
        logger.info("REDROB CANDIDATE RANKING SYSTEM")
        logger.info("=" * 60)
        
        self.load_candidates(input_file)
        self.rank_all_candidates()
        self.export_top_100(output_file)
        
        logger.info("=" * 60)
        logger.info("✓ RANKING COMPLETE")
        logger.info("=" * 60)

def main():
    """Entry point"""
    default_input = "candidates.jsonl"
    default_output = "submission.csv"

    if len(sys.argv) == 1:
        input_file = default_input
        output_file = default_output
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
        output_file = default_output
    elif len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Usage: python rank.py [input_candidates.jsonl] [output.csv]")
        print("\nExamples:")
        print("  python rank.py")
        print("  python rank.py candidates.jsonl")
        print("  python rank.py candidates.jsonl submission.csv")
        sys.exit(1)

    ranker = CandidateRanker()
    ranker.run(input_file, output_file)

if __name__ == '__main__':
    main()
