"""
Which engine answers each project's Try it page.

- AI projects (DocuMind, ShopAssist, SupportFlow, VoiceDesk, PageMind, DeskPilot): Hero's AI with the project's data.
- InsightDesk: AI writes pandas code, the sandbox runs it, AI explains the result.
- ReportBot, ForecastBoard: numbers calculated in Python, AI writes the explanation.
- BookIt: booking logic only, no AI.

Every engine returns a dict using the keys the page can show (see REPLY_KEYS in views.py).
Visitor-facing problems raise UserError; an unavailable AI raises hero_client.NotConnected.
"""
from . import booking, hero_client
from .analysis import forecast, insight, report
from .prompts import MissingInput


class UserError(ValueError):
    """A message that is safe to show the visitor."""


def _insightdesk(p):
    if not p.get('message'):
        raise UserError('Please type a question first.')
    try:
        return insight.answer(p.get('dataset', 'retail-sales'), p['message'])
    except insight.AnalysisFailed:
        raise UserError('I could not calculate that. Try asking it another way, for example "revenue by region in Q3".')


def _bookit(p):
    try:
        return booking.run(p)
    except booking.BookingError as exc:
        raise UserError(str(exc))


ENGINES = {
    'insightdesk': _insightdesk,
    'reportbot': lambda p: report.build(p.get('dataset', 'cafe-orders'), p.get('period', 'last-month')),
    'forecastboard': lambda p: forecast.build(p.get('category', 'all'), p.get('weeks', 4)),
    'bookit': _bookit,
}


def run(slug, payload):
    engine = ENGINES.get(slug)
    try:
        return engine(payload) if engine else hero_client.run(slug, payload)
    except MissingInput as exc:
        raise UserError(str(exc))
