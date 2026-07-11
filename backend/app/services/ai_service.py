"""AI service — LangChain + Google Gemini for all content generation."""

import json
import logging
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LLM initialization
# ---------------------------------------------------------------------------


def _get_llm(temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    """Create a Gemini LLM instance."""
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    api_key = os.getenv("GOOGLE_API_KEY", "")
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
    )


def _lang_instruction(language: str) -> str:
    """Return language instruction for prompts."""
    if language == "hi":
        return "Respond entirely in Hindi (Devanagari script हिन्दी). Use Hindi for all content, labels, descriptions, and category names."
    return "Respond entirely in English."


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_PLAN_SYSTEM = """You are StormShield, an expert AI monsoon preparedness advisor for Indian families.

Given the user's profile and current weather conditions, generate a personalized monsoon preparedness plan with three phases.

USER PROFILE:
{profile_json}

CURRENT WEATHER:
{weather_json}

{language_instruction}

Return ONLY a valid JSON object (no markdown, no code blocks) with this exact structure:
{{
  "phases": [
    {{
      "phase": "before",
      "title": "Before Monsoon — Preparation",
      "items": [
        {{
          "category": "Category Name",
          "description": "Specific action item",
          "priority": "high|medium|low",
          "personalized_note": "Why this matters for this specific user/family or null"
        }}
      ]
    }},
    {{
      "phase": "during",
      "title": "During Monsoon — Active Safety",
      "items": [...]
    }},
    {{
      "phase": "after",
      "title": "After Monsoon — Recovery",
      "items": [...]
    }}
  ],
  "current_phase": "{monsoon_phase_simple}",
  "profile_summary": "Brief sentence about how this plan is personalized"
}}

Generate 5-8 items per phase. Personalize based on:
- Dwelling type (ground floor = flooding risk, high-rise = wind risk, kaccha house = structural risk)
- Family composition (elderly = mobility plans, children = school safety, pets = pet supplies)
- Location (coastal = storm surge, near water = flood evacuation)
- Health conditions (asthma = air quality, mobility = evacuation planning)
- Vehicle ownership (travel safety, fuel reserves)"""

_DASHBOARD_SYSTEM = """You are StormShield, an expert AI monsoon preparedness advisor.

Given the user's profile and weather, generate dashboard summary content.

USER PROFILE:
{profile_json}

CURRENT WEATHER:
{weather_json}

{language_instruction}

Return ONLY a valid JSON object (no markdown, no code blocks) with this exact structure:
{{
  "risk_score": {{
    "score": <0-100 integer>,
    "level": "low|moderate|high|very_high",
    "explanation": "Why this score for this user"
  }},
  "checklist": {{
    "items": [
      {{
        "item": "Action item text",
        "category": "Category",
        "is_personalized": true/false,
        "reason": "Why personalized or null"
      }}
    ]
  }},
  "travel": {{
    "safety_rating": "safe|caution|avoid",
    "summary": "Brief travel safety assessment",
    "tips": ["tip 1", "tip 2", "tip 3"]
  }},
  "safety": {{
    "tips": [
      {{
        "category": "electrical|waterlogging|health|structural",
        "icon": "emoji",
        "tip": "Safety recommendation"
      }}
    ]
  }}
}}

Generate 5-6 checklist items, 3 travel tips, and 4 safety tips.
Personalize everything based on the profile — do NOT give generic advice."""

_CHAT_SYSTEM = """You are StormShield Assistant, a friendly and knowledgeable AI helper for monsoon preparedness in India.

You help users with monsoon safety questions, preparedness advice, emergency guidance, and travel advisories.

USER PROFILE:
{profile_json}

CURRENT WEATHER CONDITIONS:
{weather_json}

USER IS CURRENTLY VIEWING: {page_context}

{language_instruction}

Guidelines:
- Be concise but thorough. Use bullet points and bold text for key items.
- Always personalize advice based on the user's profile (location, family, dwelling).
- Reference current weather conditions when relevant.
- If the user asks about travel, consider their city, weather severity, and vehicle ownership.
- For emergency situations, lead with the most urgent action first.
- Use emojis sparingly for visual clarity (⚠️ for warnings, ✅ for safe, 🏠 for home tips).
- If unsure about something, say so honestly rather than guessing."""


# ---------------------------------------------------------------------------
# Generation functions
# ---------------------------------------------------------------------------


async def generate_plan(
    profile_dict: dict, weather_dict: dict, language: str = "en"
) -> dict:
    """Generate a personalized preparedness plan. Returns parsed JSON dict."""
    llm = _get_llm(temperature=0.7)
    monsoon_phase = weather_dict.get("monsoon_phase", "active_monsoon")
    phase_simple = monsoon_phase.replace("_monsoon", "").replace("active", "during")
    if phase_simple == "pre":
        phase_simple = "before"
    elif phase_simple == "post":
        phase_simple = "after"

    prompt = ChatPromptTemplate.from_messages([
        ("system", _PLAN_SYSTEM),
        ("human", "Generate my personalized monsoon preparedness plan now."),
    ])
    chain = prompt | llm | StrOutputParser()

    result = await chain.ainvoke({
        "profile_json": json.dumps(profile_dict, indent=2),
        "weather_json": json.dumps(weather_dict, indent=2),
        "language_instruction": _lang_instruction(language),
        "monsoon_phase_simple": phase_simple,
    })

    return _parse_json(result)


async def generate_dashboard(
    profile_dict: dict, weather_dict: dict, language: str = "en"
) -> dict:
    """Generate dashboard content (risk score, checklist, travel, safety)."""
    llm = _get_llm(temperature=0.5)
    prompt = ChatPromptTemplate.from_messages([
        ("system", _DASHBOARD_SYSTEM),
        ("human", "Generate my monsoon preparedness dashboard summary now."),
    ])
    chain = prompt | llm | StrOutputParser()

    result = await chain.ainvoke({
        "profile_json": json.dumps(profile_dict, indent=2),
        "weather_json": json.dumps(weather_dict, indent=2),
        "language_instruction": _lang_instruction(language),
    })

    return _parse_json(result)


async def chat_reply(
    profile_dict: dict,
    weather_dict: dict,
    message: str,
    page_context: str,
    history: list[dict],
    language: str = "en",
) -> str:
    """Generate a conversational chat reply. Returns Markdown string."""
    llm = _get_llm(temperature=0.7)

    messages: list[tuple[str, str]] = [("system", _CHAT_SYSTEM)]
    # Add conversation history
    for msg in history[-10:]:  # Keep last 10 messages to manage context
        role = "human" if msg["role"] == "user" else "ai"
        messages.append((role, msg["content"]))
    messages.append(("human", "{user_message}"))

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm | StrOutputParser()

    result = await chain.ainvoke({
        "profile_json": json.dumps(profile_dict, indent=2),
        "weather_json": json.dumps(weather_dict, indent=2),
        "page_context": page_context,
        "language_instruction": _lang_instruction(language),
        "user_message": message,
    })

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_json(text: str) -> dict:
    """Extract and parse JSON from LLM response, handling code blocks."""
    cleaned = text.strip()
    # Remove markdown code blocks if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("Failed to parse AI response as JSON: %s...", cleaned[:200])
        # Return a minimal valid structure
        return {"error": "Failed to parse AI response", "raw": cleaned[:500]}
