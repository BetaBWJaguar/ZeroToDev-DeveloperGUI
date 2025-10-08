# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Callable, Optional, Dict, Any


@dataclass
class MarkupTag:
    name: str
    has_inner_text: bool = True
    default_attrs: Optional[Dict[str, Any]] = None
    description: str = ""
    processor: Optional[Callable] = None


class MarkupManagerTags:
    EMPHASIS = MarkupTag(
        name="emphasis",
        has_inner_text=True,
        default_attrs={"level": "moderate"},
        description="Highlights a part of text with stronger intonation."
    )

    BREAK = MarkupTag(
        name="break",
        has_inner_text=False,
        default_attrs={"time": "1s"},
        description="Inserts a pause (silence) in the speech."
    )

    EMOTION = MarkupTag(
        name="emotion",
        has_inner_text=True,
        default_attrs={"type": "neutral"},
        description="Adds emotional tone to the speech such as happy, sad, angry."
    )

    PROSODY = MarkupTag(
        name="prosody",
        has_inner_text=True,
        default_attrs={"rate": "1.0", "pitch": "0"},
        description="Controls the pitch and speaking rate."
    )

    SAY_AS = MarkupTag(
        name="say-as",
        has_inner_text=True,
        default_attrs={"interpret-as": "text"},
        description="Defines how the text should be spoken (e.g., spell-out, digits, date)."
    )

    ALL_TAGS = {
        EMPHASIS.name: EMPHASIS,
        BREAK.name: BREAK,
        EMOTION.name: EMOTION,
        PROSODY.name: PROSODY,
        SAY_AS.name: SAY_AS
    }

    @classmethod
    def get_tag(cls, name: str) -> Optional[MarkupTag]:
        return cls.ALL_TAGS.get(name.lower())

    @classmethod
    def list_supported_tags(cls) -> list[str]:
        return list(cls.ALL_TAGS.keys())

    @classmethod
    def describe_all(cls) -> dict:
        return {k: v.description for k, v in cls.ALL_TAGS.items()}
