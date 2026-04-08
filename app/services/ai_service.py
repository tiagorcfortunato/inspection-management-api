import base64
import io
import json
import logging
from functools import lru_cache

from groq import AsyncGroq
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from PIL import Image
from pydantic import BaseModel

from app.core.config import settings
from app.core.enums import DamageType, SeverityLevel

logger = logging.getLogger(__name__)

MAX_IMAGE_DIMENSION = 1024
JPEG_QUALITY = 75


def compress_image_base64(image_b64: str) -> str:
    """Compress and resize image to stay within Groq API limits."""
    raw = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(raw))
    img = img.convert("RGB")

    if max(img.size) > MAX_IMAGE_DIMENSION:
        img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY)
    compressed = base64.b64encode(buf.getvalue()).decode()
    logger.info(
        f"[AI] Image compressed: {len(image_b64) // 1024}KB -> {len(compressed) // 1024}KB"
    )
    return compressed


class AIClassification(BaseModel):
    damage_type: DamageType
    severity: SeverityLevel
    rationale: str


CLASSIFICATION_PROMPT = (
    "You are a road inspection classifier. "
    "Classify the damage type and severity of the road damage. "
    "Explain your reasoning in one sentence to help a human inspector trust your decision."
    "\n\nYou MUST respond with ONLY a JSON object in this exact format, no other text:\n"
    '{"damage_type": "<pothole|crack|rutting|surface_wear>", '
    '"severity": "<low|medium|high|critical>", '
    '"rationale": "<one sentence explanation>"}'
)


class AIService:
    def __init__(self) -> None:
        # Groq SDK directly for vision (langchain-groq doesn't handle images)
        self._groq = AsyncGroq(api_key=settings.GROQ_API_KEY.get_secret_value())
        # LangChain for text-only with structured output
        self._text_llm = ChatGroq(
            model="llama-3.2-11b-vision-preview",
            api_key=settings.GROQ_API_KEY,
        ).with_structured_output(AIClassification)

    async def classify_inspection(
        self,
        notes: str | None = None,
        image_data: str | None = None,
    ) -> AIClassification:
        if image_data:
            return await self._classify_with_image(notes, image_data)
        else:
            return await self._classify_text_only(notes)

    async def _classify_with_image(
        self,
        notes: str | None,
        image_data: str,
    ) -> AIClassification:
        compressed = compress_image_base64(image_data)

        text = CLASSIFICATION_PROMPT
        if notes:
            text += f"\n\nInspection notes: {notes}"

        # Use Groq SDK directly — langchain-groq doesn't pass images properly
        response = await self._groq.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{compressed}",
                            },
                        },
                        {
                            "type": "text",
                            "text": text,
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()
        logger.info(f"[AI] Vision raw response: {raw}")

        # Extract JSON from response (handle markdown code blocks)
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        return AIClassification(**json.loads(raw))

    async def _classify_text_only(self, notes: str | None) -> AIClassification:
        text = (
            "You are a road inspection classifier. "
            "Classify the damage type and severity of the road damage. "
            "Explain your reasoning in one sentence to help a human inspector trust your decision."
        )
        if notes:
            text += f"\n\nInspection notes: {notes}"

        content = [{"type": "text", "text": text}]
        message = HumanMessage(content=content)
        return await self._text_llm.ainvoke([message])


@lru_cache(maxsize=1)
def get_ai_service() -> AIService:
    return AIService()
