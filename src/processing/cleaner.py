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
        print(f"Cleaner: {len(messages)} → {len(cleaned)} messages")
        return cleaned