import os
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder containing RAG documents
KNOWLEDGE_BASE_DIR = BASE_DIR / "rag_documents"


def load_documents():
    """
    Read all text documents from the rag_documents folder
    and return their combined content.
    """

    documents = []

    if not KNOWLEDGE_BASE_DIR.exists():
        return ""

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.txt"):
        try:
            content = file_path.read_text(encoding="utf-8")

            documents.append(
                f"Document: {file_path.name}\n"
                f"{content}"
            )

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return "\n\n".join(documents)


def get_leave_policy():
    """
    Load the leave policy document.
    """

    leave_policy_path = KNOWLEDGE_BASE_DIR / "leave_policy.txt"

    if not leave_policy_path.exists():
        return ""

    try:
        return leave_policy_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading leave policy: {e}")
        return ""