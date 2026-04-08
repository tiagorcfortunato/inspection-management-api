from functools import lru_cache

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.core.config import settings
from app.core.enums import DamageType, SeverityLevel


class AIClassification(BaseModel):
    damage_type: DamageType
    severity: SeverityLevel
    rationale: str


class AIService:
    def __init__(self) -> None:
        self._llm = ChatGroq(
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

        text = (
            "You are a road inspection classifier. "
            "Classify the damage type and severity of the road damage. "
            "Explain your reasoning in one sentence to help a human inspector trust your decision."
        )
        if notes:
            text += f"\n\nInspection notes: {notes}"

        content.append({"type": "text", "text": text})

        message = HumanMessage(content=content)
        return await self._llm.ainvoke([message])


@lru_cache(maxsize=1)
def get_ai_service() -> AIService:
    return AIService()
