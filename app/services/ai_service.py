from functools import lru_cache

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
            model="llama-3.3-70b-versatile",
            api_key=settings.GROQ_API_KEY,
        ).with_structured_output(AIClassification)

    async def classify_inspection(self, notes: str) -> AIClassification:
        prompt = (
            "You are a road inspection classifier. "
            "Given the following inspection notes, classify the damage type and severity. "
            "Explain your reasoning for this classification in one sentence "
            "to help a human inspector trust your decision.\n\n"
            f"Notes: {notes}"
        )
        return await self._llm.ainvoke(prompt)


@lru_cache(maxsize=1)
def get_ai_service() -> AIService:
    return AIService()
