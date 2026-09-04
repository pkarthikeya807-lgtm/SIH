"""
NSQF Skill Recommendation & Matching Engine.
Evaluates 7-dimensional beneficiary vector against official NSQF Qualification Packs (QPs).
Generates compatibility scores, RPL bonuses, skill gap analysis, and training center linkages.
"""

import math
from ..models import NSQFTrade, SkillCenter

# Education hierarchy ranking for prerequisite verification
EDU_RANK = {
    'None': 0,
    'Primary (5th)': 1,
    '5th Pass': 1,
    'Middle (8th)': 2,
    '8th Pass': 2,
    'Secondary (10th)': 3,
    '10th Pass': 3,
    'Higher Secondary (12th)': 4,
    '12th Pass': 4,
    'ITI / Vocational': 5,
    'ITI / Diploma': 5,
    'Diploma': 5,
    'Graduate': 6
}


class NSQFMatcher:
    """
    Core matching engine implementing weighted 7-dimension similarity scoring.
    """

    @classmethod
    def evaluate_beneficiary(cls, beneficiary):
        """
        Runs comprehensive evaluation for a Beneficiary instance or profile dictionary.
        Returns sorted recommendations, skill gaps, and PM-AJAY center affiliations.
        """
        trades = NSQFTrade.objects.all()
        if not trades.exists():
            return []

        # Extract beneficiary attributes
        edu_str = getattr(beneficiary, 'education_level', '8th Pass')
        ben_edu_rank = EDU_RANK.get(edu_str, 2)
        family_occ = getattr(beneficiary, 'family_occupation', '').lower()
        current_liv = getattr(beneficiary, 'current_livelihood', '').lower()
        primary_skills = getattr(beneficiary, 'primary_skills', [])
        if isinstance(primary_skills, str):
            primary_skills = [s.strip() for s in primary_skills.split(',')]
        primary_skills_lower = [s.lower() for s in primary_skills]

        mobility = getattr(beneficiary, 'mobility_constraint', 'Within District HQ')
        emp_pref = getattr(beneficiary, 'employment_preference', 'Self-Employed / Micro-Enterprise')
        district_econ = getattr(beneficiary, 'district_economy', '').lower()
        district_name = getattr(beneficiary, 'district', 'Varanasi')
        state_name = getattr(beneficiary, 'state', 'Uttar Pradesh')

        # Convert employment preference to a target wage_vs_self float (0.0 = wage, 1.0 = self)
        target_self_score = 0.8 if 'self' in emp_pref.lower() or 'micro' in emp_pref.lower() or 'shg' in emp_pref.lower() else 0.2

        recommendations = []

        for trade in trades:
            # 1. Educational eligibility check (Weight: 15%)
            min_edu_rank = EDU_RANK.get(trade.min_education, 2)
            if ben_edu_rank >= min_edu_rank:
                dim1_score = 100.0
                edu_gap = None
            else:
                # Penalty if under-qualified, but still calculated for bridge courses
                gap_diff = min_edu_rank - ben_edu_rank
                dim1_score = max(20.0, 100.0 - (gap_diff * 35.0))
                edu_gap = f"Requires prerequisite bridge module from {edu_str} to {trade.min_education}"

            # 2. Traditional Family Occupation Synergy / RPL Bonus (Weight: 20%)
            # Recognition of Prior Learning (RPL) gives substantial boost if heritage skill matches QP
            dim2_score = 25.0  # baseline
            rpl_applied = False
            for tag in trade.traditional_synergy_tags:
                if tag.lower() in family_occ or family_occ in tag.lower():
                    dim2_score = 100.0
                    rpl_applied = True
                    break
                elif any(word in family_occ for word in tag.lower().split()):
                    dim2_score = 80.0
                    rpl_applied = True
                    break

            # 3. Current Livelihood transferability (Weight: 10%)
            dim3_score = 40.0
            if 'helper' in current_liv or 'labor' in current_liv or 'apprentice' in current_liv:
                dim3_score = 75.0
            elif 'vendor' in current_liv or 'shop' in current_liv:
                if trade.wage_vs_self_score >= 0.6:
                    dim3_score = 90.0

            # 4. Stated Skills & Interests Affinity (Weight: 25%)
            dim4_score = 30.0
            matched_skills = []
            trade_text = f"{trade.name} {trade.sector} {trade.description} {' '.join(trade.key_modules)}".lower()
            for skill in primary_skills_lower:
                if any(kw in trade_text for kw in skill.split()):
                    matched_skills.append(skill)
            if matched_skills:
                dim4_score = min(100.0, 50.0 + (len(matched_skills) * 25.0))

            # 5. Mobility Constraint Alignment (Weight: 10%)
            dim5_score = 70.0
            if 'home-based' in mobility.lower() or 'village' in mobility.lower():
                if trade.wage_vs_self_score >= 0.7 or 'handloom' in trade.sector.lower() or 'apparel' in trade.sector.lower():
                    dim5_score = 100.0
                else:
                    dim5_score = 45.0
            else:
                dim5_score = 95.0

            # 6. Self vs Wage Employment Alignment (Weight: 10%)
            # Similarity between user preference and QP trade nature
            pref_diff = abs(trade.wage_vs_self_score - target_self_score)
            dim6_score = max(20.0, 100.0 - (pref_diff * 90.0))

            # 7. Local District Economy Demand (Weight: 10%)
            dim7_score = 40.0
            for tag in trade.district_demand_tags:
                if tag.lower() in district_econ or any(w in district_econ for w in tag.lower().split('_')):
                    dim7_score = 100.0
                    break

            # Weighted Total Score Calculation
            total_score = (
                (dim1_score * 0.15) +
                (dim2_score * 0.20) +
                (dim3_score * 0.10) +
                (dim4_score * 0.25) +
                (dim5_score * 0.10) +
                (dim6_score * 0.10) +
                (dim7_score * 0.10)
            )

            total_score = round(min(98.5, max(30.0, total_score)), 1)

            # Determine Skill Gap Analysis & Bridge Modules
            skill_gaps = []
            if edu_gap:
                skill_gaps.append(edu_gap)
            if not rpl_applied and trade.nsqf_level >= 4:
                skill_gaps.append(f"Requires 40-hour Foundational Technical Toolkit for {trade.sector}")
            if 'solar' in trade.name.lower() and not any('electric' in s for s in primary_skills_lower):
                skill_gaps.append("Basic DC/AC Circuit Safety module needed prior to on-site commissioning")

            # Identify nearby PM-AJAY Centers offering this trade
            nearby_centers = SkillCenter.objects.filter(
                trades_offered=trade,
                state__icontains=state_name
            )[:3]

            # If none in same state, pick any 2 nearest
            if not nearby_centers.exists():
                nearby_centers = SkillCenter.objects.filter(trades_offered=trade)[:2]

            center_list = [
                {
                    'id': c.center_id,
                    'name': c.name,
                    'district': c.district,
                    'state': c.state,
                    'address': c.address,
                    'hostel': c.hostel_available,
                    'contact': c.contact_phone or "+91 800-PMAJAY-SKILL"
                } for c in nearby_centers
            ]

            recommendations.append({
                'trade_id': trade.id,
                'qp_code': trade.qp_code,
                'trade_name': trade.name,
                'sector': trade.sector,
                'nsqf_level': trade.nsqf_level,
                'duration_hours': trade.duration_hours,
                'match_score': total_score,
                'rpl_eligible': rpl_applied,
                'avg_monthly_income_inr': trade.avg_monthly_income_inr,
                'wage_vs_self': 'Self-Employment / Enterprise' if trade.wage_vs_self_score >= 0.55 else 'Wage Employment',
                'dimension_breakdown': {
                    'education_fit': round(dim1_score),
                    'traditional_synergy': round(dim2_score),
                    'livelihood_continuity': round(dim3_score),
                    'skill_aptitude': round(dim4_score),
                    'mobility_fit': round(dim5_score),
                    'employment_mode_fit': round(dim6_score),
                    'district_demand_fit': round(dim7_score),
                },
                'skill_gaps': skill_gaps if skill_gaps else ["No critical skill gaps identified. Fast-track enrolment ready."],
                'key_modules': trade.key_modules,
                'nearby_centers': center_list
            })

        # Sort recommendations by highest match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations
