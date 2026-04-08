import json
import logging
from functools import lru_cache

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.core.config import settings
from app.core.enums import DamageType, SeverityLevel

logger = logging.getLogger(__name__)


class AIClassification(BaseModel):
    damage_type: DamageType
    severity: SeverityLevel
    rationale: str


CLASSIFICATION_PROMPT = (
    "You are a road inspection classifier. "
    "Classify the damage type and severity of the road damage. "
    "Explain your reasoning in one sentence to help a human inspector trust your decision."
    "\n\nYou MUST respond with ONLY a JSON object in this exact format, no other text:\n"
    '{{"damage_type": "<pothole|crack|rutting|surface_wear>", '
    '"severity": "<low|medium|high|critical>", '
    '"rationale": "<one sentence explanation>"}}'
)


class AIService:
    def __init__(self) -> None:
        self._vision_llm = ChatGroq(
            model="llama-3.2-11b-vision-preview",
            api_key=settings.GROQ_API_KEY,
        )
        self._text_llm = ChatGroq(
            model="llama-3.2-11b-vision-preview",
            api_key=settings.GROQ_API_KEY,
        ).with_structured_output(AIClassification)

    async def classify_inspection(
        self,
        notes: str | None = None,
        image_data: str | None = None,
    ) -> AIClassification:
        content = []

        if image_data:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
            })

        text = CLASSIFICATION_PROMPT
        if notes:
            text += f"\n\nInspection notes: {notes}"

        content.append({"type": "text", "text": text})
        message = HumanMessage(content=content)

        if image_data:
            # Vision model doesn't support structured output / tool calling
            # with images, so we parse JSON from the raw response instead
            response = await self._vision_llm.ainvoke([message])
            raw = response.content.strip()
            logger.info(f"[AI] Vision raw response: {raw}")
            # Extract JSON from response (handle markdown code blocks)
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
            return AIClassification(**json.loads(raw))
        else:
            return await self._text_llm.ainvoke([message])


@lru_cache(maxsize=1)
def get_ai_service() -> AIService:
    return AIService()
