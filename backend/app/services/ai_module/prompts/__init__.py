"""
提示词模块
"""

from .base import BasePrompt, PromptType
from .text_prompts import (
    CharacterDialoguePrompt,
    CharacterSystemPrompt,
    GeneralTextPrompt,
)
from .image_prompts import (
    CharacterImagePrompt,
    GeneralImagePrompt,
)
from .vision_prompts import (
    ImageAnalysisPrompt,
    ImageDescriptionPrompt,
)

__all__ = [
    "BasePrompt",
    "PromptType",
    "CharacterDialoguePrompt",
    "CharacterSystemPrompt",
    "GeneralTextPrompt",
    "CharacterImagePrompt",
    "GeneralImagePrompt",
    "ImageAnalysisPrompt",
    "ImageDescriptionPrompt",
]
