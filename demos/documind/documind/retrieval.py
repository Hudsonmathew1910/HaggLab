import json
import re
from pathlib import Path
import numpy as np

# Sample College Handbook Knowledge Base
HANDBOOK_PAGES = [
    {
        "page": 1,
        "title": "Admissions & Enrollment",
        "text": "Registration for Fall semester opens July 1st and closes August 25th. Late registration requires a $50 administrative fee. All students must submit high school transcripts and immunization records prior to course enrollment."
    },
    {
        "page": 2,
        "title": "Academic Policies & Grading",
        "text": "The grading system is A (4.0), B (3.0), C (2.0), D (1.0), and F (0.0). A minimum cumulative GPA of 2.0 is required for good academic standing. Students below 2.0 are placed on academic probation for one semester."
    },
    {
        "page": 3,
        "title": "Attendance & Leave of Absence",
        "text": "Students are expected to attend at least 80 percent of scheduled class sessions. An official leave of absence may be requested for medical or family emergencies up to two consecutive terms through the Dean of Students office."
    },
    {
        "page": 4,
        "title": "Library & Research Resources",
        "text": "The campus library is open Monday through Thursday 8 AM to 10 PM, Friday 8 AM to 6 PM, and weekends 10 AM to 5 PM. Remote students may access academic journals and databases using their student portal credentials."
    },
    {
        "page": 5,
        "title": "Tuition, Fees & Refunds",
        "text": "Full tuition refund is granted for course drops during the first two weeks of classes. A 50 percent refund is granted for weeks 3 and 4. No refunds are issued after week 4. Payment plans divide tuition across 4 equal installments."
    },
    {
        "page": 6,
        "title": "Student Code of Conduct",
        "text": "Academic integrity strictly prohibits plagiarism, cheating, and unauthorized collaboration. Violations are reviewed by the Honor Council and can result in course failure or disciplinary suspension."
    }
]

def simple_embed(text):
    """
    Deterministic TF-IDF style bag-of-words vectorizer for fast, self-contained local retrieval.
    In production/staging, this plugs directly into Gemini embedding model.
    """
    vocab = [
        'admission', 'registration', 'fall', 'august', 'july', 'fee', 'transcript', 'immunization',
        'grade', 'grading', 'gpa', 'probation', 'standing', 'fail',
        'attendance', 'leave', 'absence', 'medical', 'emergency', 'dean',
        'library', 'hours', 'weekend', 'journal', 'database', 'remote',
        'tuition', 'refund', 'drop', 'installments', 'payment',
        'honor', 'conduct', 'plagiarism', 'cheating', 'suspension'
    ]
    words = re.findall(r'\b[a-z]+\b', text.lower())
    vec = np.zeros(len(vocab), dtype=np.float32)
    for w in words:
        for idx, stem in enumerate(vocab):
            if stem in w:
                vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def query_handbook(question, threshold=0.15):
    """
    Finds the most relevant handbook section using cosine similarity.
    Strictly returns 'I do not know' if similarity is below the confidence threshold.
    """
    q_vec = simple_embed(question)
    best_sim = -1.0
    best_match = None

    for entry in HANDBOOK_PAGES:
        p_vec = simple_embed(entry['text'] + ' ' + entry['title'])
        sim = float(np.dot(q_vec, p_vec))
        if sim > best_sim:
            best_sim = sim
            best_match = entry

    if best_sim >= threshold and best_match:
        return {
            "answer": best_match['text'],
            "source_page": best_match['page'],
            "source_title": best_match['title'],
            "confidence": round(best_sim, 3),
            "status": "found"
        }
    else:
        return {
            "answer": "I do not know. This answer is not found in the uploaded college handbook.",
            "source_page": None,
            "source_title": None,
            "confidence": round(best_sim, 3),
            "status": "not_found"
        }
