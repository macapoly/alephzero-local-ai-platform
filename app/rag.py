# ============================================================
# ALEPHZERO RAG RETRIEVER
# Local Knowledge Retrieval Layer
# ============================================================

from pathlib import Path
import re


# ============================================================
# CONFIGURATION
# ============================================================

KNOWLEDGE_DIR = Path("knowledge")

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
}


# ============================================================
# LOAD KNOWLEDGE FILES
# ============================================================

def load_documents():
    """
    Load supported documents from the knowledge directory.
    """

    documents = []

    if not KNOWLEDGE_DIR.exists():
        return documents

    for file_path in KNOWLEDGE_DIR.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:

            content = file_path.read_text(
                encoding="utf-8"
            ).strip()

            if not content:
                continue

            documents.append({

                "source": str(file_path),

                "content": content

            })

        except Exception as error:

            print(
                f"RAG: Could not read {file_path}: {error}"
            )

    return documents


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text for lightweight keyword retrieval.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):
    """
    Convert text into searchable tokens.
    """

    normalized = normalize_text(text)

    if not normalized:
        return []

    return normalized.split()


# ============================================================
# CHUNK DOCUMENT
# ============================================================

def chunk_text(
    text,
    chunk_size=120,
    overlap=20
):
    """
    Split a document into overlapping word chunks.
    """

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


# ============================================================
# BUILD KNOWLEDGE INDEX
# ============================================================

def build_index():
    """
    Load documents and create searchable chunks.
    """

    documents = load_documents()

    index = []

    for document in documents:

        chunks = chunk_text(
            document["content"]
        )

        for chunk in chunks:

            index.append({

                "source":
                    document["source"],

                "content":
                    chunk,

                "tokens":
                    set(tokenize(chunk))

            })

    return index


# ============================================================
# SCORE CHUNK
# ============================================================

def score_chunk(
    query,
    chunk
):
    """
    Score a knowledge chunk against a query.

    This is intentionally lightweight.
    """

    query_tokens = set(
        tokenize(query)
    )

    chunk_tokens = chunk["tokens"]

    if not query_tokens:
        return 0

    matches = (
        query_tokens &
        chunk_tokens
    )

    return len(matches)


# ============================================================
# RETRIEVE
# ============================================================

def retrieve(
    query,
    top_k=3
):
    """
    Retrieve the most relevant knowledge chunks.
    """

    index = build_index()

    if not index:
        return []

    scored_results = []

    for chunk in index:

        score = score_chunk(
            query,
            chunk
        )

        if score <= 0:
            continue

        scored_results.append({

            "source":
                chunk["source"],

            "content":
                chunk["content"],

            "score":
                score

        })

    scored_results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return scored_results[:top_k]


# ============================================================
# FORMAT CONTEXT
# ============================================================

def build_context(
    query,
    top_k=3
):
    """
    Retrieve knowledge and format it as model context.
    """

    results = retrieve(
        query,
        top_k=top_k
    )

    if not results:
        return ""

    context_parts = []

    for result in results:

        context_parts.append(

            f"Source: {result['source']}\n"
            f"{result['content']}"

        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# RAG STATUS
# ============================================================

def rag_status():
    """
    Return basic information about the RAG knowledge base.
    """

    documents = load_documents()

    index = build_index()

    return {

        "knowledge_directory":
            str(KNOWLEDGE_DIR),

        "directory_exists":
            KNOWLEDGE_DIR.exists(),

        "documents":
            len(documents),

        "chunks":
            len(index)

    }