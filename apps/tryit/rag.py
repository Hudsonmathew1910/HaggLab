"""
RAG for the Try it projects: datasets/ files -> chunks -> Pinecone vectors -> relevant chunks for each question.

The PINECONE_INDEX index embeds the text itself (integrated llama-text-embed-v2, 1024 dimensions), so we send
plain text and one key covers both embedding and storage. Each project has its own namespace.

Upload:  python manage.py rag_ingest            (all projects)
         python manage.py rag_ingest documind   (one project)
Search:  search('documind', 'how much annual leave?') -> [{'text', 'source', 'score'}, ...]
"""
import csv
import logging
import re
import time
from functools import lru_cache
from pathlib import Path

import httpx
from django.conf import settings

from . import trace

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / 'datasets'
MAX_CHUNK = 1500        # characters; long sections are split on paragraphs


class RagUnavailable(Exception):
    """Pinecone is not configured or could not be reached. Callers fall back to the whole file."""


# ---------------------------------------------------------------------------
# What goes into each namespace
# ---------------------------------------------------------------------------
def markdown_chunks(rel_path):
    """Split a Markdown file on its ## headings; long sections are split on blank lines."""
    text = (DATA_DIR / rel_path).read_text(encoding='utf-8')
    title_match = re.match(r'#\s+(.+)', text)
    title = title_match.group(1).strip() if title_match else Path(rel_path).stem
    chunks = []
    for part in re.split(r'\n(?=##\s)', text):
        part = part.strip()
        if not part:
            continue
        heading_match = re.match(r'#{1,3}\s+(.+)', part)
        heading = heading_match.group(1).strip() if heading_match else title
        pieces, current = [], ''
        for para in part.split('\n\n'):
            if current and len(current) + len(para) > MAX_CHUNK:
                pieces.append(current)
                current = ''
            current = f'{current}\n\n{para}'.strip()
        if current:
            pieces.append(current)
        for n, piece in enumerate(pieces):
            body = piece if n == 0 else f'{heading} (continued)\n{piece}'
            chunks.append({'text': f'[{title}]\n{body}', 'source': heading})
    return chunks


def csv_chunks(rel_path, render, source):
    """One chunk per CSV row, written as readable text by `render(row)`."""
    with open(DATA_DIR / rel_path, encoding='utf-8') as f:
        return [{'text': render(row), 'source': source(row)} for row in csv.DictReader(f)]


def product_text(r):
    return (f"Product: {r['name']} (ID {r['product_id']}). Category: {r['category']} / {r['subcategory']}. "
            f"Brand: {r['brand']}. Price: {r['price_usd']} USD. Colours: {r['colours']}. "
            f"Description: {r['description']} Features: {r['features']}. "
            f"Availability: {r['availability']} ({r['stock_qty']} in stock). "
            f"Rating: {r['rating']} from {r['review_count']} reviews.")


def ticket_text(r):
    return (f"Example ticket. Customer message: {r['message']}\nTopic: {r['topic']} | Urgency: {r['urgency']}\n"
            f"Agent reply: {r['agent_reply']}")


def service_text(r):
    return ' | '.join(f'{k}: {v}' for k, v in r.items() if v)


SOURCES = {
    'documind': lambda: markdown_chunks('documind/staff_handbook.md'),
    'shopassist': lambda: csv_chunks('shopassist/products.csv', product_text, lambda r: r['name']),
    'supportflow': lambda: markdown_chunks('supportflow/support_policy.md'),
    'supportflow-tickets': lambda: csv_chunks('supportflow/tickets.csv', ticket_text,
                                              lambda r: f"Example ticket {r['ticket_id']}"),
    'voicedesk': lambda: markdown_chunks('voicedesk/clinic_faq.md')
    + csv_chunks('voicedesk/services.csv', service_text, lambda r: 'Services and fees'),
    'deskpilot': lambda: markdown_chunks('deskpilot/office_sops.md'),
}


# ---------------------------------------------------------------------------
# Pinecone (document index with integrated embedding, REST API version 2026-07)
# The index embeds the `chunk_text` field itself with llama-text-embed-v2; `title` holds the source.
# ---------------------------------------------------------------------------
API_VERSION = '2026-07'
UPSERT_BATCH = 90       # Pinecone allows 96 documents per upsert when a field is embedded
TIMEOUT = 30


def is_configured():
    return bool(getattr(settings, 'PINECONE_API_KEY', '') and getattr(settings, 'PINECONE_INDEX', ''))


def headers():
    return {'Api-Key': settings.PINECONE_API_KEY, 'Content-Type': 'application/json',
            'X-Pinecone-Api-Version': API_VERSION}


@lru_cache(maxsize=1)
def host():
    res = httpx.get(f'https://api.pinecone.io/indexes/{settings.PINECONE_INDEX}', headers=headers(), timeout=TIMEOUT)
    res.raise_for_status()
    return 'https://' + res.json()['host']


def ingest(project, reset=True):
    """Chunk one project's files and upload them; Pinecone embeds them. Returns the number of chunks stored."""
    if not is_configured():
        raise RagUnavailable('PINECONE_API_KEY or PINECONE_INDEX is not set')
    chunks = SOURCES[project]()
    if reset:  # remove old chunks first, so a smaller file leaves no leftovers
        httpx.delete(f'{host()}/namespaces/{project}', headers=headers(), timeout=TIMEOUT)
    docs = [{'_id': f'{project}-{n:04d}', 'title': c['source'], 'chunk_text': c['text']} for n, c in enumerate(chunks)]
    for start in range(0, len(docs), UPSERT_BATCH):
        for attempt in range(3):
            res = httpx.post(f'{host()}/namespaces/{project}/documents/upsert', headers=headers(),
                             json={'documents': docs[start:start + UPSERT_BATCH]}, timeout=120)
            if res.status_code == 404 and attempt < 2:  # namespace still being deleted
                time.sleep(2)
                continue
            if res.status_code >= 400:
                raise RagUnavailable(f'upload failed (HTTP {res.status_code}): {res.text[:300]}')
            break
    return len(docs)


def count(project):
    res = httpx.post(f'{host()}/describe_index_stats', headers=headers(), json={}, timeout=TIMEOUT)
    res.raise_for_status()
    return res.json().get('namespaces', {}).get(project, {}).get('vectorCount', 0)


def search(project, query, top_k=None):
    """The most relevant chunks for a question. Raises RagUnavailable so callers can fall back."""
    if not is_configured():
        raise RagUnavailable('not configured')
    top_k = top_k or settings.RAG_TOP_K.get(project, 5)
    started = time.perf_counter()
    body = {'score_by': [{'type': 'embed', 'fields': ['chunk_text'], 'query': query[:2000]}],
            'top_k': top_k, 'include_fields': ['title', 'chunk_text']}
    try:
        res = httpx.post(f'{host()}/namespaces/{project}/documents/search', headers=headers(), json=body,
                         timeout=TIMEOUT)
        res.raise_for_status()
        matches = res.json().get('matches', [])
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        logger.warning('Pinecone search failed for %s: %s', project, type(exc).__name__)
        trace.show(f'   Pinecone search failed ({type(exc).__name__}); using the whole file instead')
        raise RagUnavailable(type(exc).__name__) from exc
    hits, seen = [], set()
    for m in matches:
        text = m.get('chunk_text', '')
        key = re.sub(r'\W+', ' ', text.split('Agent reply:')[0]).strip().lower()[60:260]  # skip near-duplicate examples
        if key in seen:
            continue
        seen.add(key)
        hits.append({'text': text, 'source': m.get('title', ''), 'score': round(m.get('_score') or 0, 3)})
    if not hits:
        trace.show(f'   Pinecone namespace "{project}" is empty; run: python manage.py rag_ingest {project}')
        raise RagUnavailable('empty namespace')
    trace.show(f'   Pinecone search ({project}): {len(hits)} chunks in {time.perf_counter() - started:.1f}s, '
               f'best match {hits[0]["score"]} ({hits[0]["source"]})',
               [f"{h['score']}  {h['source']}" for h in hits])
    return hits


def context(project, query, fallback):
    """Relevant chunks from Pinecone as one text block; the whole file (`fallback()`) if Pinecone is unavailable."""
    try:
        hits = search(project, query)
    except RagUnavailable:
        trace.show('   Using the whole data file (no RAG)')
        return fallback()
    return '\n\n---\n\n'.join(h['text'] for h in hits)
