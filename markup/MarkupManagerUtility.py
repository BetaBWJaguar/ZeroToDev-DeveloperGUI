# -*- coding: utf-8 -*-
import re
from dataclasses import dataclass, field
from markup.MarkupManagerTags import MarkupManagerTags
from logs_manager.LogsHelperManager import LogsHelperManager
from logs_manager.LogsManager import LogsManager


@dataclass
class TTSToken:
    type: str
    value: str = ""
    attrs: dict = field(default_factory=dict)


class MarkupManagerUtility:
    def __init__(self):
        self.logger = LogsManager.get_logger("MarkupManagerUtility")
        supported_tags = "|".join(MarkupManagerTags.list_supported_tags())
        self.TAG_PATTERN = re.compile(
            rf"<({supported_tags})(.*?)>(.*?)</\1>|<({supported_tags})(.*?)\/>",
            re.DOTALL | re.IGNORECASE
        )

    def parse(self, text: str) -> list[TTSToken]:
        tokens = []
        last_end = 0

        for match in self.TAG_PATTERN.finditer(text):
            start, end = match.span()
            if start > last_end:
                tokens.append(TTSToken("text", text[last_end:start]))

            tag_name = (match.group(1) or match.group(4) or "").lower()
            attrs = self._parse_attrs(match.group(2) or match.group(5))
            inner = match.group(3) or ""

            tokens.append(TTSToken(tag_name, inner.strip(), attrs))
            last_end = end

        if last_end < len(text):
            tokens.append(TTSToken("text", text[last_end:]))

        LogsHelperManager.log_debug(self.logger, "MARKUP_PARSED", {
            "tokens": len(tokens),
            "raw_length": len(text)
        })
        return tokens

    def _parse_attrs(self, raw_attrs: str) -> dict:
        attrs = {}
        for part in raw_attrs.split():
            if "=" in part:
                k, v = part.split("=", 1)
                attrs[k.strip()] = v.strip('"\'')
        return attrs

    def debug_tokens(self, tokens: list[TTSToken]):
        for t in tokens:
            LogsHelperManager.log_debug(self.logger, "TOKEN", {
                "type": t.type,
                "value": t.value[:50],
                "attrs": t.attrs
            })
