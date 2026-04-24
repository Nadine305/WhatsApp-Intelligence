# """
# graph.py
# --------
# The LangGraph pipeline that connects every step of the system.

# Pipeline flow:
#   collect → filter → clean → embed → cluster → label → save → done

# Each step is a LangGraph node. State flows between nodes as a typed dict.
# """

# from __future__ import annotations
# from typing import TypedDict, Any
# from datetime import datetime

# from langgraph.graph import StateGraph, END


# # ── State Schema ──────────────────────────────────────────────────────────────

# class PipelineState(TypedDict):
#     # Inputs
#     mode: str                    # "count" or "time_range"
#     count: int | None            # Used when mode="count"
#     start_time: datetime | None  # Used when mode="time_range"
#     end_time: datetime | None    # Used when mode="time_range"

#     # Intermediate state
#     raw_messages: list[dict]
#     filtered_messages: list[dict]
#     cleaned_messages: list[dict]
#     embeddings: Any              # np.ndarray
#     clustered_messages: list[dict]
#     grouped_clusters: dict[int, list[dict]]
#     cluster_labels: dict[int, dict]  # {cluster_id: {label, description}}

#     # Output
#     interests_saved: int
#     errors: list[str]


# # ── Pipeline Builder ──────────────────────────────────────────────────────────

# def build_pipeline(db_manager) -> Any:
#     """
#     Builds and compiles the LangGraph pipeline.

#     Args:
#         db_manager: DatabaseManager instance

#     Returns:
#         Compiled LangGraph app ready to invoke.
#     """
#     from src.ingestion.collector import WhatsAppCollector
#     from src.ingestion.filters import MessageFilter
#     from src.processing.cleaner import TextCleaner
#     from src.clustering.embedder import MessageEmbedder
#     from src.clustering.clusterer import MessageClusterer
#     from src.intelligence.labeler import ClusterLabeler

#     # Instantiate components
#     collector = WhatsAppCollector(db_manager)
#     msg_filter = MessageFilter()
#     cleaner = TextCleaner()
#     embedder = MessageEmbedder()
#     clusterer = MessageClusterer()
#     labeler = ClusterLabeler()

#     # ── Node Functions ────────────────────────────────────────────────────────

#     def node_collect(state: PipelineState) -> PipelineState:
#         """Step 1: Collect messages from DB based on mode."""
#         print("\n📥 [1/7] Collecting messages ...")
#         try:
#             if state["mode"] == "count":
#                 messages = collector.collect_by_count(state["count"])
#             elif state["mode"] == "time_range":
#                 messages = collector.collect_by_time_range(
#                     state["start_time"], state["end_time"]
#                 )
#             else:
#                 raise ValueError(f"Unknown mode: {state['mode']}")

#             return {**state, "raw_messages": messages}
#         except Exception as e:
#             return {**state, "raw_messages": [], "errors": state["errors"] + [str(e)]}

#     def node_filter(state: PipelineState) -> PipelineState:
#         """Step 2: Filter out noise, duplicates, too-short messages."""
#         print("\n🔍 [2/7] Filtering messages ...")
#         if not state["raw_messages"]:
#             print("⚠️  No messages to filter.")
#             return {**state, "filtered_messages": []}
#         filtered = msg_filter.run(state["raw_messages"])
#         return {**state, "filtered_messages": filtered}

#     def node_clean(state: PipelineState) -> PipelineState:
#         """Step 3: Normalize and clean message text."""
#         print("\n🧹 [3/7] Cleaning text ...")
#         if not state["filtered_messages"]:
#             return {**state, "cleaned_messages": []}
#         cleaned = cleaner.clean_batch(state["filtered_messages"])
#         return {**state, "cleaned_messages": cleaned}

#     def node_embed(state: PipelineState) -> PipelineState:
#         """Step 4: Convert text to semantic vectors."""
#         print("\n🔢 [4/7] Embedding messages ...")
#         if not state["cleaned_messages"]:
#             return {**state, "embeddings": None}
#         messages, embeddings = embedder.embed(state["cleaned_messages"])
#         return {**state, "cleaned_messages": messages, "embeddings": embeddings}

#     def node_cluster(state: PipelineState) -> PipelineState:
#         """Step 5: Group messages into clusters."""
#         print("\n📊 [5/7] Clustering ...")
#         if state["embeddings"] is None or not state["cleaned_messages"]:
#             return {**state, "clustered_messages": [], "grouped_clusters": {}}
#         clustered = clusterer.cluster(state["cleaned_messages"], state["embeddings"])
#         grouped = clusterer.group_by_cluster(clustered)
#         return {**state, "clustered_messages": clustered, "grouped_clusters": grouped}

#     def node_label(state: PipelineState) -> PipelineState:
#         """Step 6: Ask Claude to name each cluster."""
#         print("\n🏷️  [6/7] Labeling clusters with Claude ...")
#         if not state["grouped_clusters"]:
#             return {**state, "cluster_labels": {}}
#         labels = labeler.label_all_clusters(state["grouped_clusters"])
#         return {**state, "cluster_labels": labels}

#     def node_save(state: PipelineState) -> PipelineState:
#         """Step 7: Persist interests and user links to the database."""
#         print("\n💾 [7/7] Saving to database ...")
#         saved_count = 0

#         for cluster_id, label_info in state["cluster_labels"].items():
#             messages_in_cluster = state["grouped_clusters"].get(cluster_id, [])
#             if not messages_in_cluster:
#                 continue

#             # Save interest
#             interest_id = db_manager.add_interest(
#                 label=label_info["label"],
#                 description=label_info["description"],
#             )
#             if interest_id is None:
#                 continue

#             # Link each user to this interest
#             for msg in messages_in_cluster:
#                 db_manager.link_user_to_interest(
#                     user_id=msg["user_id"],
#                     interest_id=interest_id,
#                     confidence=0.85,   # Fixed confidence for now; can be improved with HDBSCAN scores
#                 )
#                 # Mark message as processed
#                 db_manager.mark_as_processed(msg["message_id"])

#             saved_count += 1

#         print(f"✅ Saved {saved_count} interest groups to database.")
#         return {**state, "interests_saved": saved_count}

#     # ── Guard: skip remaining steps if no messages ────────────────────────────

#     def should_continue(state: PipelineState) -> str:
#         if not state.get("filtered_messages"):
#             print("⚠️  No messages passed filtering. Ending pipeline early.")
#             return "end"
#         return "continue"

#     # ── Build Graph ───────────────────────────────────────────────────────────

#     graph = StateGraph(PipelineState)

#     graph.add_node("collect", node_collect)
#     graph.add_node("filter", node_filter)
#     graph.add_node("clean", node_clean)
#     graph.add_node("embed", node_embed)
#     graph.add_node("cluster", node_cluster)
#     graph.add_node("label", node_label)
#     graph.add_node("save", node_save)

#     graph.set_entry_point("collect")
#     graph.add_edge("collect", "filter")

#     # Conditional edge: if no messages after filter, stop
#     graph.add_conditional_edges(
#         "filter",
#         should_continue,
#         {"continue": "clean", "end": END},
#     )

#     graph.add_edge("clean", "embed")
#     graph.add_edge("embed", "cluster")
#     graph.add_edge("cluster", "label")
#     graph.add_edge("label", "save")
#     graph.add_edge("save", END)

#     return graph.compile()
from __future__ import annotations
from typing import TypedDict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END


class PipelineState(TypedDict):
    mode: str
    count: int | None
    start_time: datetime | None
    end_time: datetime | None
    raw_messages: list[dict]
    filtered_messages: list[dict]
    cleaned_messages: list[dict]
    embeddings: Any
    clustered_messages: list[dict]
    grouped_clusters: dict[int, list[dict]]
    cluster_labels: dict[int, dict]
    interests_saved: int
    errors: list[str]


def build_pipeline(db_manager) -> Any:
    from src.ingestion.collector import WhatsAppCollector
    from src.ingestion.filters import MessageFilter
    from src.processing.cleaner import TextCleaner
    from src.clustering.embedder import MessageEmbedder
    from src.clustering.clusterer import MessageClusterer
    from src.intelligence.labeler import ClusterLabeler

    collector = WhatsAppCollector(db_manager)
    msg_filter = MessageFilter()
    cleaner = TextCleaner()
    embedder = MessageEmbedder()
    clusterer = MessageClusterer()
    labeler = ClusterLabeler()

    def node_collect(state):
        print("\n📥 [1/7] Collecting messages ...")
        try:
            if state["mode"] == "count":
                messages = collector.collect_by_count(state["count"])
            else:
                messages = collector.collect_by_time_range(state["start_time"], state["end_time"])
            return {**state, "raw_messages": messages}
        except Exception as e:
            return {**state, "raw_messages": [], "errors": state["errors"] + [str(e)]}

    def node_filter(state):
        print("\n🔍 [2/7] Filtering messages ...")
        if not state["raw_messages"]:
            print("⚠️  No messages to filter.")
            return {**state, "filtered_messages": []}
        filtered = msg_filter.run(state["raw_messages"])
        return {**state, "filtered_messages": filtered}

    def node_clean(state):
        print("\n🧹 [3/7] Cleaning text ...")
        if not state["filtered_messages"]:
            return {**state, "cleaned_messages": []}
        cleaned = cleaner.clean_batch(state["filtered_messages"])
        return {**state, "cleaned_messages": cleaned}

    def node_embed(state):
        print("\n🔢 [4/7] Embedding messages ...")
        if not state["cleaned_messages"]:
            return {**state, "embeddings": None}
        messages, embeddings = embedder.embed(state["cleaned_messages"])
        return {**state, "cleaned_messages": messages, "embeddings": embeddings}

    def node_cluster(state):
        print("\n📊 [5/7] Clustering ...")
        if state["embeddings"] is None:
            return {**state, "clustered_messages": [], "grouped_clusters": {}}
        clustered = clusterer.cluster(state["cleaned_messages"], state["embeddings"])
        grouped = clusterer.group_by_cluster(clustered)
        return {**state, "clustered_messages": clustered, "grouped_clusters": grouped}

    def node_label(state):
        print("\n🏷️  [6/7] Labeling clusters with Groq ...")
        if not state["grouped_clusters"]:
            return {**state, "cluster_labels": {}}
        labels = labeler.label_all_clusters(state["grouped_clusters"])
        return {**state, "cluster_labels": labels}

    def node_save(state):
        print("\n💾 [7/7] Saving to database ...")
        saved_count = 0
        for cluster_id, label_info in state["cluster_labels"].items():
            messages_in_cluster = state["grouped_clusters"].get(cluster_id, [])
            if not messages_in_cluster:
                continue
            interest_id = db_manager.add_interest(
                label=label_info["label"],
                description=label_info["description"],
            )
            if interest_id is None:
                continue
            for msg in messages_in_cluster:
                db_manager.link_user_to_interest(
                    user_id=msg["user_id"],
                    interest_id=interest_id,
                    confidence=0.85,
                )
                db_manager.mark_as_processed(msg["message_id"])
            saved_count += 1
        print(f"✅ Saved {saved_count} interest groups.")
        return {**state, "interests_saved": saved_count}

    def should_continue(state):
        if not state.get("filtered_messages"):
            return "end"
        return "continue"

    graph = StateGraph(PipelineState)
    graph.add_node("collect", node_collect)
    graph.add_node("filter", node_filter)
    graph.add_node("clean", node_clean)
    graph.add_node("embed", node_embed)
    graph.add_node("cluster", node_cluster)
    graph.add_node("label", node_label)
    graph.add_node("save", node_save)

    graph.set_entry_point("collect")
    graph.add_edge("collect", "filter")
    graph.add_conditional_edges("filter", should_continue, {"continue": "clean", "end": END})
    graph.add_edge("clean", "embed")
    graph.add_edge("embed", "cluster")
    graph.add_edge("cluster", "label")
    graph.add_edge("label", "save")
    graph.add_edge("save", END)

    return graph.compile()