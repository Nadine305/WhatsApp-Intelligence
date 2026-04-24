# """
# cleaner.py
# ----------
# Normalizes raw message text so that the embedding model gets clean input.

# Steps:
#   1. Strip leading/trailing whitespace
#   2. Remove URLs
#   3. Remove emojis
#   4. Collapse repeated characters (e.g. "heeello" → "hello")
#   5. Normalize Arabic text (optional, very useful for Arabic WhatsApp msgs)
#   6. Lowercase (for non-Arabic text)
#   7. Collapse multiple spaces/newlines
# """

# import re


# # ── Regex Patterns ────────────────────────────────────────────────────────────
# URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
# REPEATED_CHARS = re.compile(r"(.)\1{2,}")   # 3+ same chars in a row → keep 2
# MULTI_SPACE = re.compile(r"\s+")


# class TextCleaner:
#     """
#     Cleans a single message string. Stateless — all methods are pure functions.
#     """

#     def clean(self, text: str) -> str:
#         """
#         Full cleaning pipeline.

#         Args:
#             text: Raw message content

#         Returns:
#             Cleaned text string, or empty string if nothing remains.
#         """
#         text = self._strip(text)
#         text = self._remove_urls(text)
#         text = self._remove_emojis(text)
#         text = self._collapse_repeated(text)
#         text = self._normalize_arabic(text)
#         text = self._collapse_spaces(text)
#         return text.strip()

#     def clean_batch(self, messages: list[dict]) -> list[dict]:
#         """
#         Cleans the 'content' field of each message dict in-place.
#         Drops messages whose cleaned content becomes empty.

#         Args:
#             messages: List of dicts with 'content' key.

#         Returns:
#             List of dicts with cleaned 'content'. Empty results are dropped.
#         """
#         cleaned = []
#         for msg in messages:
#             clean_text = self.clean(msg["content"])
#             if clean_text:
#                 cleaned.append({**msg, "content": clean_text})
#         print(f"🧹 Cleaner: {len(messages)} → {len(cleaned)} messages after cleaning")
#         return cleaned

#     # ── Private Methods ───────────────────────────────────────────────────────

#     def _strip(self, text: str) -> str:
#         return text.strip()

#     def _remove_urls(self, text: str) -> str:
#         return URL_PATTERN.sub("", text)

#     def _remove_emojis(self, text: str) -> str:
#         """
#         Remove emoji characters. Uses the 'emoji' library if available,
#         otherwise falls back to a Unicode range regex.
#         """
#         try:
#             import emoji
#             return emoji.replace_emoji(text, replace="")
#         except ImportError:
#             # Fallback: strip common emoji unicode ranges
#             emoji_pattern = re.compile(
#                 "["
#                 "\U0001F600-\U0001F64F"  # emoticons
#                 "\U0001F300-\U0001F5FF"  # symbols & pictographs
#                 "\U0001F680-\U0001F6FF"  # transport & map
#                 "\U0001F1E0-\U0001F1FF"  # flags
#                 "\U00002702-\U000027B0"
#                 "\U000024C2-\U0001F251"
#                 "]+",
#                 flags=re.UNICODE,
#             )
#             return emoji_pattern.sub("", text)

#     def _collapse_repeated(self, text: str) -> str:
#         """Reduce 3+ repeated chars to 2: 'yesss' → 'yess'"""
#         return REPEATED_CHARS.sub(r"\1\1", text)

#     def _normalize_arabic(self, text: str) -> str:
#         """
#         Normalize common Arabic character variants so the embedder
#         treats them as the same token.

#         Examples:
#           أ إ آ ا → ا
#           ة → ه
#           ى → ي
#         """
#         # Normalize Alef variants → bare Alef
#         text = re.sub(r"[إأآ]", "ا", text)
#         # Normalize Taa Marbuta → Haa
#         text = re.sub(r"ة", "ه", text)
#         # Normalize Alef Maqsura → Yaa
#         text = re.sub(r"ى", "ي", text)
#         # Remove Arabic Tatweel (kashida)
#         text = re.sub(r"ـ", "", text)
#         return text

#     def _collapse_spaces(self, text: str) -> str:
#         return MULTI_SPACE.sub(" ", text)
import re

class TextCleaner:

    def clean(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        text = re.sub(r"[إأآ]", "ا", text)
        text = re.sub(r"ة", "ه", text)
        text = re.sub(r"ى", "ي", text)
        text = re.sub(r"ـ", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def clean_batch(self, messages: list[dict]) -> list[dict]:
        cleaned = []
        for msg in messages:
            clean_text = self.clean(msg["content"])
            if clean_text:
                cleaned.append({**msg, "content": clean_text})
        print(f"🧹 Cleaner: {len(messages)} → {len(cleaned)} messages")
        return cleaned