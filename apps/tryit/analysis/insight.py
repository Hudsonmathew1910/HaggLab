"""
InsightDesk: ask a table a question in plain English.

1. Hero's AI writes pandas code for the question, from the table's schema (it never sees the rows).
2. The code runs in the sandbox on the real table. If it fails, the AI gets one retry with the error.
3. Hero's AI explains the result in plain words, using only the calculated numbers.
The visitor sees the explanation, the result table and the code.
"""
import json
import re

from .. import hero_client, system_prompts, trace
from . import datasets, sandbox

CODE_RULES = system_prompts.INSIGHT_CODE
EXPLAIN_RULES = system_prompts.INSIGHT_EXPLAIN


class AnalysisFailed(Exception):
    pass


def cannot_answer(content):
    """If the AI said the table cannot answer, return (reason, suggestion); otherwise None."""
    text = (content or '').strip()
    if '```' in text or not text.upper().startswith('CANNOT:'):
        return None
    reason, _, suggestion = text[len('CANNOT:'):].partition('| TRY:')
    return reason.strip(), suggestion.strip()


def cannot_reply(table_key, reason, suggestion):
    text = f"This data can't answer that: {reason}"
    if suggestion:
        text += f'\n\nYou could ask instead: "{suggestion}"'
    return {'text': text, 'source': f"Checked against {datasets.TABLES[table_key]['label']}"}


def extract_code(content):
    match = re.search(r'```(?:python)?\s*(.*?)```', content or '', re.S)
    return (match.group(1) if match else content or '').strip()


def answer(table_key, question):
    schema = datasets.schema(table_key)
    messages = [
        {'role': 'system', 'content': CODE_RULES},
        {'role': 'user', 'content': f'{schema}\n\n<question>{question}</question>'},
    ]
    trace.show('2. Step A: AI writes pandas code (it gets only the column list, never the rows)')
    content = hero_client.chat(messages, temperature=0)
    refusal = cannot_answer(content)
    if refusal:
        trace.show('3. AI says this table cannot answer the question; telling the visitor why')
        return cannot_reply(table_key, *refusal)
    code = extract_code(content)
    trace.show('3. Step B: code runs in the sandbox on the real table', code)
    try:
        result = sandbox.run(table_key, code)
    except sandbox.SandboxError as first_error:
        trace.show('   Code failed, asking the AI to fix it once', str(first_error))
        messages += [
            {'role': 'assistant', 'content': f'```python\n{code}\n```'},
            {'role': 'user', 'content': f'That code failed: {first_error}. Fix it and follow the rules.'},
        ]
        content = hero_client.chat(messages, temperature=0)
        refusal = cannot_answer(content)
        if refusal:
            return cannot_reply(table_key, *refusal)
        code = extract_code(content)
        try:
            result = sandbox.run(table_key, code)
        except sandbox.SandboxError as exc:
            raise AnalysisFailed(str(exc)) from exc

    trace.show('4. Calculated result', {'columns': result['columns'], 'rows': result['rows'][:10]})
    trace.show('5. Step C: AI explains the result in plain words')
    preview = json.dumps({'columns': result['columns'], 'rows': result['rows'][:30]})
    reply = hero_client.parse_reply(hero_client.chat([
        {'role': 'system', 'content': EXPLAIN_RULES},
        {'role': 'user', 'content': f'<question>{question}</question>\n<result>{preview}</result>'},
    ], temperature=0.2))
    return {
        'text': reply.get('text', ''),
        'table': {'columns': result['columns'], 'rows': result['rows']},
        'source': f"Calculated from {datasets.TABLES[table_key]['label']}",
        'code': code,
    }
