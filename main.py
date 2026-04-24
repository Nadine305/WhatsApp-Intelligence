# """
# main.py
# -------
# CLI entry point for the WhatsApp Intelligence pipeline.

# Usage examples:

#   # Analyze the last 50 messages
#   python main.py --mode count --count 50

#   # Analyze messages from a specific time range
#   python main.py --mode time_range --start "2024-04-01 00:00:00" --end "2024-04-21 23:59:59"

#   # Run with default (last 100 messages)
#   python main.py
# """

# import argparse
# from datetime import datetime

# from src.storage.db_manager import DatabaseManager
# from src.intelligence.graph import build_pipeline


# def parse_args():
#     parser = argparse.ArgumentParser(
#         description="WhatsApp Intelligence — cluster messages into interest groups"
#     )
#     parser.add_argument(
#         "--mode",
#         choices=["count", "time_range"],
#         default="count",
#         help="Collection mode: 'count' or 'time_range' (default: count)",
#     )
#     parser.add_argument(
#         "--count",
#         type=int,
#         default=100,
#         help="Number of recent messages to analyze (used with --mode count)",
#     )
#     parser.add_argument(
#         "--start",
#         type=str,
#         default=None,
#         help="Start datetime for time range, format: 'YYYY-MM-DD HH:MM:SS'",
#     )
#     parser.add_argument(
#         "--end",
#         type=str,
#         default=None,
#         help="End datetime for time range, format: 'YYYY-MM-DD HH:MM:SS'",
#     )
#     return parser.parse_args()


# def main():
#     args = parse_args()

#     print("=" * 60)
#     print("  📱 WhatsApp Intelligence Pipeline")
#     print("=" * 60)

#     # ── Validate Arguments ────────────────────────────────────────────────────
#     start_time = None
#     end_time = None

#     if args.mode == "time_range":
#         if not args.start or not args.end:
#             print("❌ --start and --end are required when using --mode time_range")
#             print("   Example: --start '2024-04-01 00:00:00' --end '2024-04-21 23:59:59'")
#             return
#         try:
#             start_time = datetime.strptime(args.start, "%Y-%m-%d %H:%M:%S")
#             end_time = datetime.strptime(args.end, "%Y-%m-%d %H:%M:%S")
#         except ValueError as e:
#             print(f"❌ Invalid datetime format: {e}")
#             return

#     # ── Setup ─────────────────────────────────────────────────────────────────
#     print("\n🔌 Connecting to database ...")
#     db = DatabaseManager()

#     print("🔧 Building pipeline ...")
#     pipeline = build_pipeline(db)

#     # ── Initial State ─────────────────────────────────────────────────────────
#     initial_state = {
#         "mode": args.mode,
#         "count": args.count,
#         "start_time": start_time,
#         "end_time": end_time,
#         "raw_messages": [],
#         "filtered_messages": [],
#         "cleaned_messages": [],
#         "embeddings": None,
#         "clustered_messages": [],
#         "grouped_clusters": {},
#         "cluster_labels": {},
#         "interests_saved": 0,
#         "errors": [],
#     }

#     # ── Run ───────────────────────────────────────────────────────────────────
#     print(f"\n🚀 Running pipeline in '{args.mode}' mode ...")
#     if args.mode == "count":
#         print(f"   → Analyzing last {args.count} messages")
#     else:
#         print(f"   → Time range: {start_time} → {end_time}")

#     final_state = pipeline.invoke(initial_state)

#     # ── Summary ───────────────────────────────────────────────────────────────
#     print("\n" + "=" * 60)
#     print("  ✅ Pipeline Complete")
#     print("=" * 60)
#     print(f"  Raw messages collected : {len(final_state['raw_messages'])}")
#     print(f"  After filtering        : {len(final_state['filtered_messages'])}")
#     print(f"  After cleaning         : {len(final_state['cleaned_messages'])}")
#     print(f"  Clusters found         : {len(final_state['grouped_clusters'])}")
#     print(f"  Interests saved to DB  : {final_state['interests_saved']}")

#     if final_state["errors"]:
#         print(f"\n⚠️  Errors: {final_state['errors']}")

#     if final_state["cluster_labels"]:
#         print("\n📋 Discovered Interest Groups:")
#         for cid, info in final_state["cluster_labels"].items():
#             n = len(final_state["grouped_clusters"].get(cid, []))
#             print(f"   [{cid}] {info['label']} ({n} messages)")
#             print(f"        → {info['description']}")


# if __name__ == "__main__":
#     main()

import argparse
from datetime import datetime
from src.storage.db_manager import DatabaseManager
from src.intelligence.graph import build_pipeline


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["count", "time_range"], default="count")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    print("=" * 50)
    print("  📱 WhatsApp Intelligence Pipeline")
    print("=" * 50)

    start_time = None
    end_time = None

    if args.mode == "time_range":
        start_time = datetime.strptime(args.start, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(args.end, "%Y-%m-%d %H:%M:%S")

    print("\n🔌 Connecting to database ...")
    db = DatabaseManager()

    print("🔧 Building pipeline ...")
    pipeline = build_pipeline(db)

    initial_state = {
        "mode": args.mode,
        "count": args.count,
        "start_time": start_time,
        "end_time": end_time,
        "raw_messages": [],
        "filtered_messages": [],
        "cleaned_messages": [],
        "embeddings": None,
        "clustered_messages": [],
        "grouped_clusters": {},
        "cluster_labels": {},
        "interests_saved": 0,
        "errors": [],
    }

    print(f"\n🚀 Running pipeline in '{args.mode}' mode ...")
    final_state = pipeline.invoke(initial_state)

    print("\n" + "=" * 50)
    print("  ✅ Pipeline Complete")
    print("=" * 50)
    print(f"  Raw messages     : {len(final_state['raw_messages'])}")
    print(f"  After filtering  : {len(final_state['filtered_messages'])}")
    print(f"  Clusters found   : {len(final_state['grouped_clusters'])}")
    print(f"  Interests saved  : {final_state['interests_saved']}")

    if final_state["cluster_labels"]:
        print("\n📋 Discovered Interests:")
        for cid, info in final_state["cluster_labels"].items():
            n = len(final_state["grouped_clusters"].get(cid, []))
            print(f"   [{cid}] {info['label']} ({n} messages)")
            print(f"        → {info['description']}")


if __name__ == "__main__":
    main()