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
    print(" WhatsApp Intelligence Pipeline")
    print("=" * 50)

    start_time = None
    end_time = None

    if args.mode == "time_range":
        start_time = datetime.strptime(args.start, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(args.end, "%Y-%m-%d %H:%M:%S")

    print("\nConnecting to database ...")
    db = DatabaseManager()

    print("Building pipeline ...")
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

    print(f"\nRunning pipeline in '{args.mode}' mode ...")
    final_state = pipeline.invoke(initial_state)

    print("\n" + "=" * 50)
    print("  Pipeline Complete")
    print("=" * 50)
    print(f"  Raw messages     : {len(final_state['raw_messages'])}")
    print(f"  After filtering  : {len(final_state['filtered_messages'])}")
    print(f"  Clusters found   : {len(final_state['grouped_clusters'])}")
    print(f"  Interests saved  : {final_state['interests_saved']}")

    if final_state["cluster_labels"]:
        print("\n Discovered Interests:")
        for cid, info in final_state["cluster_labels"].items():
            n = len(final_state["grouped_clusters"].get(cid, []))
            print(f"   [{cid}] {info['label']} ({n} messages)")
            print(f"        → {info['description']}")


if __name__ == "__main__":
    main()