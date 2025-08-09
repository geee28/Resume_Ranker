import io, os, re, tempfile
from typing import List, Tuple
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from pypdf import PdfReader
import docx


def clean_text(s):
    s = s or ""
    s = s.replace("\x00", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def read_job_description_from_text(text):
    """Provide the job description directly as a string."""
    return clean_text(text)


def read_file_to_text(filepath):
    """
    Reads a .txt, .pdf, or .docx file from disk and returns its cleaned text content.

    Args:
        filepath (str): Path to the file

    Returns:
        str: Extracted and cleaned text content
    """
    # Ensure file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    name = filepath.lower()

    # --- TXT ---
    if name.endswith(".txt"):
        with open(filepath, "rb") as f:
            return clean_text(f.read().decode("utf-8", errors="ignore"))

    # --- PDF ---
    if name.endswith(".pdf"):
        if PdfReader is None:
            raise ImportError("pypdf is not installed.")
        with open(filepath, "rb") as f:
            reader = PdfReader(f)
            pages = []
            for p in reader.pages:
                try:
                    pages.append(p.extract_text() or "")
                except Exception:
                    pass
        return clean_text("\n".join(pages))

    # --- DOCX ---
    if name.endswith(".docx") or name.endswith(".doc"):
        if docx is None:
            raise ImportError("python-docx is not installed.")
        document = docx.Document(filepath)
        return clean_text("\n".join([para.text for para in document.paragraphs]))

    # --- Unsupported ---
    raise ValueError(f"Unsupported file format: {filepath}")



# Trying another embedding model

EMBED_MODEL_NAME = "BAAI/bge-m3"


def add_prefix(text, is_query):
    # Works well with bge/gte lines too
    text = (text or "").strip()
    return f"query: {text}" if is_query else f"passage: {text}"
    # If you preferred e5-style exactly:
    # return f"search_query: {text}" if is_query else f"search_document: {text}"


def load_embedder(model_name=EMBED_MODEL_NAME):
    return SentenceTransformer(model_name, trust_remote_code=True)


def embed_texts(model, texts):
    """Embeds and L2-normalizes texts so cosine ~ dot."""
    """Nomic embed model returns 768 dimension long vector"""
    embs = model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
    embs = np.array(embs)
    return embs


def why_fit_summary(job_text, resume_text):
    pass


def rank_candidates(job_description, candidates, top_k=3):
    """
    Rank candidates by cosine similarity to the job description.

    Args:
      job_description: str
      candidates: list of (name_or_id, resume_text)
      top_k: number of top candidates to return

    Returns:
      DataFrame with columns: Name/ID, Similarity
    """

    model = load_embedder(EMBED_MODEL_NAME)
    q = [add_prefix(job_description, is_query=True)]
    docs = [add_prefix(text, is_query=False) for _, text in candidates]

    q_emb = embed_texts(model, q)
    doc_embs = embed_texts(model, docs)

    sims = cosine_similarity(q_emb, doc_embs)[0]
    order = np.argsort(sims)[::-1]

    rows = []
    for idx in order[:top_k]:
        name, resume = candidates[idx]
        rows.append({
            "Name/ID": name,
            "Similarity": float(sims[idx]),
        })
    return pd.DataFrame(rows)
