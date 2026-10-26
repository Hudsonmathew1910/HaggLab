import json
from pathlib import Path
from django.core.management.base import BaseCommand
from insightdesk.engine import query_sales_data

class Command(BaseCommand):
    help = 'Run evaluation suite on 15 spreadsheet queries and record exact score'

    def handle(self, *args, **options):
        eval_path = Path(__file__).resolve().parent.parent.parent.parent / 'eval' / 'questions.json'
        with open(eval_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)

        total = len(questions)
        correct = 0
        misses = []

        self.stdout.write(f"Running InsightDesk evaluation on {total} questions...")

        for q in questions:
            res = query_sales_data(q['question'])
            if q['should_succeed']:
                if res['status'] == 'success' and str(res['answer']) == q['expected_answer']:
                    correct += 1
                else:
                    misses.append({
                        "id": q['id'],
                        "question": q['question'],
                        "expected": q['expected_answer'],
                        "actual": res['answer']
                    })
            else:
                if res['status'] == 'unsupported':
                    correct += 1
                else:
                    misses.append({
                        "id": q['id'],
                        "question": q['question'],
                        "expected": "unsupported",
                        "actual": res['status']
                    })

        self.stdout.write(self.style.SUCCESS(f"\nEvaluation Complete: {correct} of {total} questions answered correctly."))
        if misses:
            self.stdout.write(self.style.WARNING(f"Misses ({len(misses)}):"))
            for m in misses:
                self.stdout.write(f"  - #{m['id']} '{m['question']}': {m}")
        else:
            self.stdout.write("Zero misses recorded.")
