"""
Short, clear service names for the five solutions, used in navigation and service cards.
Keyed by Solution slug. The long copy (headline, problem, steps) stays in the Solution model.
"""

SERVICES = {
    'answer-customers-staff-faster': {
        'name': 'AI assistants and support tools',
        'desc': 'Answer customer and staff questions from your own documents.',
        'icon': 'chat',
    },
    'help-visitors-buy-or-book': {
        'name': 'Shopping and booking systems',
        'desc': 'Help visitors find the right product and book a free slot.',
        'icon': 'cart',
    },
    'turn-numbers-into-decisions': {
        'name': 'Data analysis and forecasting',
        'desc': 'Ask your spreadsheets questions and see demand before it comes.',
        'icon': 'chart',
    },
    'remove-repetitive-work': {
        'name': 'Automation tools',
        'desc': 'Reports, file tasks and copy-paste work, done by a tool.',
        'icon': 'repeat',
    },
    'turn-idea-into-working-product': {
        'name': 'First product builds',
        'desc': 'Turn one core workflow into a working first version.',
        'icon': 'layers',
    },
}


def service_for(solution):
    """Return the service card data for a Solution, falling back to its own title."""
    meta = SERVICES.get(solution.slug, {})
    return {
        'name': meta.get('name', solution.title),
        'desc': meta.get('desc', solution.problem),
        'icon': meta.get('icon', 'box'),
    }
