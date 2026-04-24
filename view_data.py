# from src.storage.db_manager import DatabaseManager
# from sqlalchemy import text

# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# db = DatabaseManager()

# def view_messages():
#     with db.engine.connect() as conn:
#         rows = conn.execute(text("""
#             SELECT u.name, m.content, m.timestamp, m.is_processed
#             FROM messages m
#             JOIN users u ON m.user_id = u.user_id
#             ORDER BY m.timestamp DESC
#         """)).fetchall()

#     print(f"\n Total messages: {len(rows)}")
#     print("-" * 60)
#     for row in rows:
#         status = "✅" if row[3] else "⏳"
#         name = row[0] if row[0] else "Unknown"
#         content = row[1] if row[1] else ""
#         print(f"{status} {name}: {content}")
#     # for row in rows:
#     #     status = "✅" if row[3] else "⏳"
#     #     print(f"{status} {row[0]}: {row[1]}")

# def view_interests():
#     with db.engine.connect() as conn:
#         rows = conn.execute(text("""
#             SELECT u.name, i.cluster_label, i.description, ui.confidence_score
#             FROM user_interests ui
#             JOIN users u ON ui.user_id = u.user_id
#             JOIN interests i ON ui.interest_id = i.interest_id
#             ORDER BY i.cluster_label
#         """)).fetchall()

#     print(f"\n Total interest groups: {len(rows)}")
#     print("-" * 60)
#     for row in rows:
#         print(f" {row[0]} → [{row[1]}] {row[2]} (confidence: {row[3]})")

# if __name__ == "__main__":
#     print("=" * 60)
#     print(" WhatsApp Intelligence — Data Viewer")
#     print("=" * 60)
#     view_messages()
#     view_interests()
# from src.storage.db_manager import DatabaseManager
# from sqlalchemy import text

# db = DatabaseManager()

# def view_messages(f):
#     with db.engine.connect() as conn:
#         rows = conn.execute(text("""
#             SELECT u.name, m.content, m.timestamp, m.is_processed
#             FROM messages m
#             JOIN users u ON m.user_id = u.user_id
#             ORDER BY m.timestamp DESC
#         """)).fetchall()

#     print(f"\n Total messages: {len(rows)}", file=f)
#     print("-" * 60, file=f)
#     for row in rows:
#         status = "✅" if row[3] else "⏳"
#         name = row[0] if row[0] else "Unknown"
#         content = row[1] if row[1] else ""
#         print(f"{status} {name}: {content}", file=f)

# def view_interests(f):
#     with db.engine.connect() as conn:
#         rows = conn.execute(text("""
#             SELECT u.name, i.cluster_label, i.description, ui.confidence_score
#             FROM user_interests ui
#             JOIN users u ON ui.user_id = u.user_id
#             JOIN interests i ON ui.interest_id = i.interest_id
#             ORDER BY i.cluster_label
#         """)).fetchall()

#     print(f"\n Total interest groups: {len(rows)}", file=f)
#     print("-" * 60, file=f)
#     for row in rows:
#         print(f" {row[0]} → [{row[1]}] {row[2]} (confidence: {row[3]})", file=f)

# if __name__ == "__main__":
#     with open("output.txt", "w", encoding="utf-8") as f:
#         print("=" * 60, file=f)
#         print(" WhatsApp Intelligence — Data Viewer", file=f)
#         print("=" * 60, file=f)
#         view_messages(f)
#         view_interests(f)

#     print("✅ Done! Open output.txt to see results")
from src.storage.db_manager import DatabaseManager
from sqlalchemy import text

db = DatabaseManager()

def view_messages(f):
    with db.engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT u.name, u.phone_number, m.content, m.timestamp, m.is_processed
            FROM messages m
            JOIN users u ON m.user_id = u.user_id
            ORDER BY m.timestamp DESC
        """)).fetchall()

    print(f"\n Total messages: {len(rows)}", file=f)
    print("-" * 60, file=f)
    for row in rows:
        status = "" if row[4] else ""
        name = row[0] if row[0] else "Unknown"
        phone = row[1] if row[1] else ""
        content = row[2] if row[2] else ""
        print(f"{status} {name} ({phone}): {content}", file=f)

def view_interests(f):
    with db.engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT i.cluster_label, i.description, u.name, u.phone_number
            FROM user_interests ui
            JOIN users u ON ui.user_id = u.user_id
            JOIN interests i ON ui.interest_id = i.interest_id
            ORDER BY i.cluster_label
        """)).fetchall()

    print(f"\n  Interest Groups:", file=f)
    print("-" * 60, file=f)

    current_label = None
    for row in rows:
        if row[0] != current_label:
            current_label = row[0]
            print(f"\n [{row[0]}]", file=f)
            print(f"   {row[1]}", file=f)
        print(f"    {row[2]} —  {row[3]}", file=f)

if __name__ == "__main__":
    with open("output.txt", "w", encoding="utf-8") as f:
        print("=" * 60, file=f)
        print(" WhatsApp Intelligence — Data Viewer", file=f)
        print("=" * 60, file=f)
        view_messages(f)
        view_interests(f)

    print(" Done! Open output.txt to see results")