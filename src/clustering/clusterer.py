# """
# clusterer.py
# ------------
# Groups messages into clusters WITHOUT predefined labels using HDBSCAN.

# Why HDBSCAN?
#   - No need to specify number of clusters (K) in advance
#   - Handles noise naturally (label = -1 for outliers)
#   - Works well with semantic embeddings
#   - Detects clusters of varying density

# Output per message:
#   - cluster_id: integer (-1 = noise/unclustered)

# The clusterer also reduces dimensionality first with UMAP for better
# cluster quality (optional but recommended for high-dim embeddings).
# """

# import numpy as np

# try:
#     import hdbscan
#     HDBSCAN_AVAILABLE = True
# except ImportError:
#     HDBSCAN_AVAILABLE = False

# try:
#     from umap import UMAP
#     UMAP_AVAILABLE = True
# except ImportError:
#     UMAP_AVAILABLE = False


# # ── Config ────────────────────────────────────────────────────────────────────
# UMAP_N_COMPONENTS = 10       # Reduce to 10 dims before clustering
# UMAP_N_NEIGHBORS = 15
# UMAP_MIN_DIST = 0.0

# HDBSCAN_MIN_CLUSTER_SIZE = 3   # Minimum messages to form a cluster
# HDBSCAN_MIN_SAMPLES = 2        # Controls noise sensitivity


# class MessageClusterer:
#     """
#     Clusters message embeddings into topical groups.
#     """

#     def cluster(
#         self,
#         messages: list[dict],
#         embeddings: np.ndarray,
#     ) -> list[dict]:
#         """
#         Assigns a cluster_id to each message.

#         Args:
#             messages:   List of message dicts
#             embeddings: np.ndarray shape (N, dim)

#         Returns:
#             List of message dicts, each with an added 'cluster_id' key.
#             cluster_id == -1 means the message is noise (no clear group).
#         """
#         if len(messages) < HDBSCAN_MIN_CLUSTER_SIZE:
#             print("⚠️  Too few messages to cluster. Assigning all to cluster 0.")
#             for msg in messages:
#                 msg["cluster_id"] = 0
#             return messages

#         # ── Step 1: Dimensionality Reduction (optional but improves quality) ──
#         reduced = self._reduce(embeddings)

#         # ── Step 2: HDBSCAN Clustering ────────────────────────────────────────
#         labels = self._hdbscan_cluster(reduced)

#         # ── Step 3: Attach labels to messages ─────────────────────────────────
#         for msg, label in zip(messages, labels):
#             msg["cluster_id"] = int(label)

#         n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
#         n_noise = list(labels).count(-1)
#         print(f"📊 Clustering: {n_clusters} clusters found, {n_noise} noise messages")

#         return messages

#     def group_by_cluster(self, messages: list[dict]) -> dict[int, list[dict]]:
#         """
#         Groups a list of clustered messages by cluster_id.

#         Returns:
#             Dict mapping cluster_id → list of message dicts.
#             Excludes noise (cluster_id = -1).
#         """
#         groups: dict[int, list[dict]] = {}
#         for msg in messages:
#             cid = msg.get("cluster_id", -1)
#             if cid == -1:
#                 continue  # Skip noise
#             groups.setdefault(cid, []).append(msg)
#         return groups

#     # ── Private ───────────────────────────────────────────────────────────────

#     def _reduce(self, embeddings: np.ndarray) -> np.ndarray:
#         """UMAP dimensionality reduction. Falls back to PCA if UMAP not installed."""
#         if UMAP_AVAILABLE:
#             print("📉 Reducing dimensions with UMAP ...")
#             reducer = UMAP(
#                 n_components=min(UMAP_N_COMPONENTS, embeddings.shape[1]),
#                 n_neighbors=min(UMAP_N_NEIGHBORS, len(embeddings) - 1),
#                 min_dist=UMAP_MIN_DIST,
#                 metric="cosine",
#                 random_state=42,
#             )
#             return reducer.fit_transform(embeddings)
#         else:
#             print("📉 UMAP not installed. Using PCA fallback ...")
#             from sklearn.decomposition import PCA
#             n = min(UMAP_N_COMPONENTS, embeddings.shape[0] - 1, embeddings.shape[1])
#             pca = PCA(n_components=n, random_state=42)
#             return pca.fit_transform(embeddings)

#     def _hdbscan_cluster(self, data: np.ndarray) -> np.ndarray:
#         """Run HDBSCAN. Falls back to AgglomerativeClustering if not installed."""
#         if HDBSCAN_AVAILABLE:
#             clusterer = hdbscan.HDBSCAN(
#                 min_cluster_size=HDBSCAN_MIN_CLUSTER_SIZE,
#                 min_samples=HDBSCAN_MIN_SAMPLES,
#                 metric="euclidean",
#                 cluster_selection_method="eom",
#             )
#             return clusterer.fit_predict(data)
#         else:
#             print("⚠️  hdbscan not installed. Using AgglomerativeClustering fallback ...")
#             from sklearn.cluster import AgglomerativeClustering
#             n_clusters = max(2, len(data) // 10)
#             model = AgglomerativeClustering(n_clusters=n_clusters)
#             return model.fit_predict(data)
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