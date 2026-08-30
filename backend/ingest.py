"""Standalone ingestion CLI.

Usage (from the backend/ directory):

    python ingest.py            # only index if the collection is empty
    python ingest.py --force    # reindex everything
"""
import argparse
import os
import sys

from dotenv import load_dotenv

os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.rag.ingestion import ingest_documents  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Index the ErrorLens knowledge base into ChromaDB.")
    parser.add_argument("--force", action="store_true", help="Re-index even if data already exists.")
    args = parser.parse_args()

    summary = ingest_documents(force=args.force)
    print(summary)
    if summary.get("skipped_reason"):
        sys.exit(0)


if __name__ == "__main__":
    main()