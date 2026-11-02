"""
Pick the passages that answer a question: BM25 keyword ranking over Haggi's live passages (knowledge.py).

Why not Pinecone: Haggi's passages change whenever the admin changes, and there are only about a hundred of them.
Ranking them in memory is instant, free, needs no re-upload and is never out of date.
Titles count extra, and a few common words people use ("cost", "price", "how much") map to the pricing passages.
"""
import math
import re
from collections import Counter

WORD = re.compile(r"[a-z0-9]+")
STOP = set('a about an and are as at be but by can do does for from how i if in is it its me my of on or our so that '
           'the their them there these they this to us was we what when where which who will with you your tell me'.split())
# Words people ask with -> words the passages use
SYNONYMS = {
    'cost': ['price', 'pricing', 'packages'], 'costs': ['price', 'pricing', 'packages'],
    'much': ['price'], 'charge': ['price'], 'fee': ['price'], 'fees': ['price'], 'budget': ['price', 'packages'],
    'cheap': ['basic', 'price'], 'quote': ['price', 'scope'], 'rupees': ['price'], 'inr': ['price'],
    'chatbot': ['chatbots', 'assistant'], 'bot': ['chatbots', 'assistant'], 'rag': ['documents', 'assistant'],
    'app': ['apps', 'mvp', 'web'], 'website': ['web', 'apps', 'mvp'], 'mvp': ['saas', 'first', 'version'],
    'ml': ['machine', 'learning', 'models'], 'predict': ['forecast', 'models'], 'forecast': ['predictions'],
    'automate': ['automation', 'python'], 'script': ['python', 'programs'], 'excel': ['csv', 'spreadsheets'],
    'demo': ['try', 'sample'], 'try': ['demo', 'sample'], 'refund': ['terms', 'payment'], 'pay': ['payment', 'terms'],
    'privacy': ['data', 'privacy'], 'secure': ['security'], 'safe': ['security'], 'data': ['data', 'security'],
    'time': ['days', 'delivery', 'timeline'], 'long': ['days', 'delivery'], 'deadline': ['delivery', 'days'],
    'contact': ['start', 'message', 'reply'], 'hire': ['start', 'order', 'fiverr'], 'order': ['packages', 'fiverr'],
    'company': ['hagglab', 'studio'], 'studio': ['hagglab'], 'business': ['hagglab', 'studio'],
    'team': ['studio', 'hagglab'], 'who': ['hagglab', 'studio'], 'yourself': ['hagglab', 'studio'],
    'located': ['hagglab'], 'location': ['hagglab'],
    'heros': ['product', 'heros'], 'baymax': ['heros'], 'zeno': ['heros'], 'infinsight': ['heros'],
    'own': ['ownership', 'code'], 'owner': ['ownership'], 'support': ['support', 'handover'],
}


def tokens(text):
    out = []
    for w in WORD.findall(text.lower()):
        if w in STOP:
            continue
        out.append(w[:-1] if len(w) > 4 and w.endswith('s') else w)  # light plural folding
    return out


class Index:
    def __init__(self, chunks, k1=1.4, b=0.7):
        self.chunks = chunks
        self.k1, self.b = k1, b
        self.docs = [Counter(tokens(c['title']) * 3 + tokens(c['text'])) for c in chunks]  # title counts 3x
        # The name after "Project: ", "Service: ", "Product: " ...: a question that names it gets that passage first
        self.names = [c['title'].split(': ', 1)[-1].lower() for c in chunks]
        self.lens = [sum(d.values()) for d in self.docs]
        self.avg = (sum(self.lens) / len(self.lens)) if self.lens else 1
        df = Counter(w for d in self.docs for w in d)
        n = len(self.docs)
        self.idf = {w: math.log(1 + (n - f + 0.5) / (f + 0.5)) for w, f in df.items()}

    def search(self, question, top=6):
        q_text = ' '.join(question.lower().split())
        q = tokens(question)
        expanded = Counter(q)
        for w in q:
            for extra in SYNONYMS.get(w, []):
                expanded[extra.rstrip('s') if len(extra) > 4 else extra] += 0.5
        scores = []
        for i, d in enumerate(self.docs):
            s = 0.0
            for w, weight in expanded.items():
                f = d.get(w)
                if not f:
                    continue
                s += weight * self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.lens[i] / self.avg))
            name = self.names[i]
            if len(name) > 3 and name in q_text:
                s += 8.0
            kind = self.chunks[i].get('kind')
            if COMPANY_QUESTION.search(q_text):
                if kind == 'company':
                    s += 15.0
                elif self.chunks[i]['title'].startswith('About'):
                    s += 6.0
            if kind == 'overview' and LIST_QUESTION.search(q_text):
                topic = name.split()[-1]  # "all our services" -> "services"
                if topic.rstrip('s') in q_text:
                    s += 12.0
            if s > 0:
                scores.append((s, i))
        scores.sort(reverse=True)
        return [self.chunks[i] | {'score': round(s, 2)} for s, i in scores[:top]]


# "Tell me about the company", "who are you", "what does HaggLab do", "about your studio" ...
COMPANY_QUESTION = re.compile(
    r"\b(company|studio|agency|business|hagglab|yourselves|yourself|your team)\b"
    r"|\bwho (are|is) (you|hagglab|behind)\b|\bwhat (do|does) (you|hagglab|your)\b|\babout (you|us)\b")

# "What services do you offer", "which projects can I try", "list your products", "all services" ...
LIST_QUESTION = re.compile(r'\b(what|which|list|all|any|show|kinds?|types?|offer|have|provide)\b')

_cache = {'chunks': None, 'index': None}


def search(question, top=6):
    """The best passages for a question, from the live knowledge."""
    from . import knowledge
    _version, chunks = knowledge.get_chunks()
    if _cache['chunks'] is not chunks:  # rebuilt after a content change
        _cache['chunks'], _cache['index'] = chunks, Index(chunks)
    return _cache['index'].search(question, top)
