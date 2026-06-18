"""
AlphaAlign — LLM Prompt Templates.

Structured prompts for different analysis types.
All prompts receive structured JSON data from the scoring engine.
"""

SYSTEM_PROMPT = """You are AlphaAlign, a senior AI strategy advisor. You provide structured, 
professional strategic analysis for enterprise AI architecture decisions. Your analysis should 
be suitable for executive leadership and board-level presentations.

You analyze data from a structured decision-support tool that evaluates three AI architecture outcomes:
1. Strong Vendor Commitment — standardize around a primary vendor ecosystem
2. Hybrid AI Operating Model — vendor platforms + independent orchestration layer  
3. Independent AI Control Model — business-controlled AI orchestration

Your role is ONLY to interpret results. Never recalculate scores. Present insights as a consultant would."""


def build_executive_summary_prompt(analysis_data: dict) -> str:
    import json
    data_str = json.dumps(analysis_data, indent=2)
    return f"""Based on the following AlphaAlign assessment results, generate a concise executive summary 
suitable for C-suite leadership. The summary should cover:

1. The recommended AI architecture position and why
2. Key scoring highlights and score gaps between alternatives
3. Top strategic drivers that influenced the recommendation
4. Leadership alignment findings (where the team agrees and disagrees)
5. Any strategic importance overrides that affected the final scores
6. 3-4 recommended next steps

Assessment Data:
{data_str}

Format the summary in clear sections with headers. Keep it to 400-600 words. 
Use a confident, advisory tone appropriate for a boardroom presentation."""


def build_risk_analysis_prompt(analysis_data: dict) -> str:
    import json
    data_str = json.dumps(analysis_data, indent=2)
    return f"""Based on the following AlphaAlign assessment results, generate a risk analysis covering:

1. Key risks associated with the recommended architecture position
2. Risks of NOT adopting the recommended position
3. Transition risks if moving from current state to recommended state
4. Vendor dependency risks
5. Capability and readiness gaps
6. Governance and compliance risks
7. Risk mitigation recommendations

Assessment Data:
{data_str}

Be specific and actionable. Format with clear headers and bullet points."""


def build_alignment_interpretation_prompt(analysis_data: dict) -> str:
    import json
    data_str = json.dumps(analysis_data, indent=2)
    return f"""Based on the following leadership alignment data from an AlphaAlign assessment, 
provide an interpretation that:

1. Identifies where the leadership team is strongly aligned
2. Highlights areas of significant disagreement
3. Suggests which disagreements are most important to resolve
4. Recommends facilitation topics for a leadership workshop
5. Notes any role-based patterns (e.g., technical leaders vs. business leaders)

Assessment Data:
{data_str}

Write this as a consultant's briefing to the assessment facilitator. Be diplomatic but direct."""


def build_roadmap_prompt(analysis_data: dict) -> str:
    import json
    data_str = json.dumps(analysis_data, indent=2)
    return f"""Based on the following AlphaAlign assessment results, generate a detailed 
implementation roadmap covering 0-24 months with:

1. Phase 0-3 months: Foundation and quick wins
2. Phase 3-6 months: Pilot and validation
3. Phase 6-12 months: Scale and embed
4. Phase 12-24 months: Mature and optimize

For each phase, include:
- Key objectives
- Critical activities
- Success criteria
- Risks to monitor
- Governance checkpoints

Assessment Data:
{data_str}

Format as a structured roadmap table with clear phases and milestones."""


ANALYSIS_PROMPTS = {
    "executive_summary": build_executive_summary_prompt,
    "risk_analysis": build_risk_analysis_prompt,
    "alignment_interpretation": build_alignment_interpretation_prompt,
    "roadmap": build_roadmap_prompt,
}
