import numpy as np
from sklearn.cluster import AgglomerativeClustering

class MessageClusterer:

    def cluster(self, messages: list[dict], embeddings: np.ndarray) -> list[dict]:
        if len(messages) < 2:
            for msg in messages:
                msg["cluster_id"] = 0
            return messages

        n_clusters = max(2, len(messages) // 2)
        n_clusters = min(n_clusters, len(messages))
        
        model = AgglomerativeClustering(n_clusters=n_clusters)
        labels = model.fit_predict(embeddings)

        for msg, label in zip(messages, labels):
            msg["cluster_id"] = int(label)

        print(f"📊 Clustering: {len(set(labels))} clusters found")
        return messages

    def group_by_cluster(self, messages: list[dict]) -> dict:
        groups = {}
        for msg in messages:
            cid = msg.get("cluster_id", -1)
            if cid == -1:
                continue
            groups.setdefault(cid, []).append(msg)
        return groups