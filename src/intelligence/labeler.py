import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 300
MAX_SAMPLES_PER_CLUSTER = 10


class ClusterLabeler:

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GEMINI_API_KEY"))

    def label_cluster(self, cluster_id: int, messages: list[dict]) -> dict:
        samples = messages[:MAX_SAMPLES_PER_CLUSTER]
        sample_texts = "\n".join(f"- {msg['content']}" for msg in samples)

        prompt = f"""You are analyzing a group of WhatsApp messages clustered by topic.

Messages:
{sample_texts}

Respond ONLY with a valid JSON object, no markdown, no explanation:
{{
  "label": "Short interest label (2-4 words)",
  "description": "One sentence describing what people in this group are interested in."
}}"""

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            result = json.loads(raw)
            print(f"Cluster {cluster_id} → '{result['label']}'")
            return result
        except Exception as e:
            print(f"Groq error: {e}")
            return {"label": f"Group {cluster_id}", "description": "Uncategorized"}

    def label_all_clusters(self, grouped: dict) -> dict:
        results = {}
        for cluster_id, messages in grouped.items():
            results[cluster_id] = self.label_cluster(cluster_id, messages)
        return results