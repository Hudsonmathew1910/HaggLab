"""
Short, clear service names for the five solutions, used in navigation and service cards.
Keyed by Solution slug. The long copy (headline, problem, steps) stays in the Solution model.
"""

SERVICES = {
    'ai-chatbots-rag-assistants': {
        'name': 'AI chatbots and RAG assistants',
        'desc': 'Assistants that answer from your own documents and data, with the source shown.',
        'icon': 'chat',
        'art': 'service-ai-chatbots',
    },
    'saas-mvps-ai-web-apps': {
        'name': 'SaaS MVPs and AI web apps',
        'desc': 'Turn one core workflow into a working first version.',
        'icon': 'layers',
        'art': 'service-saas-mvp',
    },
    'nlp-machine-learning-models': {
        'name': 'NLP and machine learning models',
        'desc': 'Sort your text and predict from your data, with the error stated.',
        'icon': 'chart',
        'art': 'service-nlp-ml',
    },
    'python-programs-automation': {
        'name': 'Python programs and automation',
        'desc': 'Reports, file tasks and copy-paste work, done by a tool.',
        'icon': 'repeat',
        'art': 'service-python-automation',
    },
    'ai-integration-support': {
        'name': 'AI integration and support',
        'desc': 'Add AI to the app you already have, and keep it running.',
        'icon': 'gauge',
        'art': 'service-ai-integration',
    },
}

# Slugs of the five services before the 2026-10-31 rename, so old links still work
OLD_SLUGS = {
    'answer-customers-staff-faster': 'ai-chatbots-rag-assistants',
    'turn-idea-into-working-product': 'saas-mvps-ai-web-apps',
    'turn-numbers-into-decisions': 'nlp-machine-learning-models',
    'remove-repetitive-work': 'python-programs-automation',
    'help-visitors-buy-or-book': 'ai-integration-support',
}


def service_for(solution):
    """Return the service card data for a Solution, falling back to its own title."""
    meta = SERVICES.get(solution.slug, {})
    return {
        'name': meta.get('name', solution.title),
        'desc': meta.get('desc', solution.problem),
        'icon': meta.get('icon', 'box'),
        'art': meta.get('art', ''),
    }
