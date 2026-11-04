from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.models import AIBrainstormRequest, AIDecomposeRequest, AIGenerateRequest
from backend.ai_agent import ai_agent

router = APIRouter(prefix="/api/ai", tags=["AI Creative Studio"])

@router.post("/brainstorm")
async def brainstorm_creative_concept(data: AIBrainstormRequest):
    """Generates rich brand identity, channel names, taglines, visual vibes."""
    system_prompt = (
        "You are an expert creative director. For the user's project concept, generate: "
        "1. 3 memorable project/channel names. "
        "2. An evocative tagline. "
        "3. Distinctive visual identity (color palette hex codes, lighting style, cinematography). "
        "4. Target audience profile. "
        "5. Unique selling proposition (USP)."
    )
    user_prompt = f"Concept: {data.concept}\nCategory: {data.category}\nDesired Vibe: {data.vibe}"
    result = await ai_agent.generate_completion(system_prompt, user_prompt)
    return {
        "concept": data.concept,
        "brainstorm_output": result
    }

@router.post("/decompose")
async def decompose_goal_into_tasks(data: AIDecomposeRequest):
    """Decomposes a large creative milestone into actionable tasks."""
    system_prompt = (
        "Break down this creative goal into 4 specific, actionable production tasks. "
        "For each task provide: title, category (pre-production, production, post-production, distribution), "
        "priority (high, medium, low), and brief description."
    )
    result = await ai_agent.generate_completion(system_prompt, f"Goal: {data.goal}")
    return {
        "goal": data.goal,
        "tasks_breakdown": result
    }

@router.post("/script")
async def generate_creative_script(data: AIGenerateRequest):
    """Generates a cinematic video script or podcast outline."""
    system_prompt = (
        "You are an award-winning scriptwriter. Write an engaging, atmospheric script "
        "with timestamps, [VISUAL] directions (camera angles, macro shots, grading notes), "
        "[AUDIO] directions (Foley cues, binaural layers), and [NARRATION] dialogue."
    )
    result = await ai_agent.generate_completion(system_prompt, data.prompt)
    return {
        "project_id": data.project_id,
        "script_content": result
    }
