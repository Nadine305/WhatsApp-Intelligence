# """
# filters.py
# ----------
# Filters a raw list of message dicts BEFORE they enter the clustering pipeline.

# Responsibilities:
#   - Remove duplicates (same content from same user)
#   - Remove messages that are too short to be meaningful
#   - Remove pure-emoji or URL-only messages
#   - Optionally filter by language
# """

# import re


# # ── Config ────────────────────────────────────────────────────────────────────
# MIN_WORD_COUNT = 3          # Messages with fewer words are dropped
# ALLOWED_LANGUAGES = None    # e.g. ["ar", "en"] to restrict. None = allow all


# class MessageFilter:
#     """
#     Stateless filter: takes a list of message dicts and returns a cleaned list.
#     """

#     def run(self, messages: list[dict]) -> list[dict]:
#         """
#         Apply all filters in sequence.

#         Args:
#             messages: List of dicts with at least keys: message_id, user_id, content

#         Returns:
#             Filtered list of message dicts.
#         """
#         before = len(messages)

#         messages = self._remove_duplicates(messages)
#         messages = self._remove_too_short(messages)
#         messages = self._remove_noise_only(messages)

#         if ALLOWED_LANGUAGES:
#             messages = self._filter_by_language(messages)

#         after = len(messages)
#         print(f"🔍 Filter: {before} messages → {after} kept ({before - after} dropped)")
#         return messages

#     # ── Individual Filters ────────────────────────────────────────────────────

#     def _remove_duplicates(self, messages: list[dict]) -> list[dict]:
#         """
#         Removes messages where (user_id, content) pair was already seen.
#         Keeps the first occurrence.
#         """
#         seen = set()
#         unique = []
#         for msg in messages:
#             key = (msg["user_id"], msg["content"].strip().lower())
#             if key not in seen:
#                 seen.add(key)
#                 unique.append(msg)
#         return unique

#     def _remove_too_short(self, messages: list[dict]) -> list[dict]:
#         """Drop messages with fewer than MIN_WORD_COUNT words."""
#         return [
#             msg for msg in messages
#             if len(msg["content"].split()) >= MIN_WORD_COUNT
#         ]

#     def _remove_noise_only(self, messages: list[dict]) -> list[dict]:
#         """
#         Drop messages that are ONLY:
#           - Emojis
#           - URLs
#           - Numbers / punctuation
#         """
#         # Pattern: URL
#         url_pattern = re.compile(r"https?://\S+|www\.\S+")
#         # Pattern: anything that's not a letter (unicode-aware)
#         letters_pattern = re.compile(r"\p{L}", re.UNICODE) if False else re.compile(r"[a-zA-Z\u0600-\u06FF\u0750-\u077F]")

#         def has_real_words(text: str) -> bool:
#             cleaned = url_pattern.sub("", text).strip()
#             return bool(letters_pattern.search(cleaned))

#         return [msg for msg in messages if has_real_words(msg["content"])]

#     def _filter_by_language(self, messages: list[dict]) -> list[dict]:
#         """
#         Keep only messages whose detected language is in ALLOWED_LANGUAGES.
#         Requires: pip install langdetect
#         """
#         try:
#             from langdetect import detect, LangDetectException
#         except ImportError:
#             print("⚠️  langdetect not installed — skipping language filter")
#             return messages

#         filtered = []
#         for msg in messages:
#             try:
#                 lang = detect(msg["content"])
#                 if lang in ALLOWED_LANGUAGES:
#                     filtered.append(msg)
#             except LangDetectException:
#                 pass  # Drop undetectable language messages
#         return filtered
import re

MIN_WORD_COUNT = 3

class MessageFilter:

    def run(self, messages: list[dict]) -> list[dict]:
        before = len(messages)
        messages = self._remove_duplicates(messages)
        messages = self._remove_too_short(messages)
        messages = self._remove_noise_only(messages)
        after = len(messages)
        print(f"🔍 Filter: {before} → {after} kept")
        return messages

    def _remove_duplicates(self, messages):
        seen = set()
        unique = []
        for msg in messages:
            key = (msg["user_id"], msg["content"].strip().lower())
            if key not in seen:
                seen.add(key)
                unique.append(msg)
        return unique

    def _remove_too_short(self, messages):
        return [m for m in messages if len(m["content"].split()) >= MIN_WORD_COUNT]

    def _remove_noise_only(self, messages):
        url_pattern = re.compile(r"https?://\S+|www\.\S+")
        letters = re.compile(r"[a-zA-Z\u0600-\u06FF]")
        def has_words(text):
            cleaned = url_pattern.sub("", text).strip()
            return bool(letters.search(cleaned))
        return [m for m in messages if has_words(m["content"])]