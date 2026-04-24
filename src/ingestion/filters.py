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