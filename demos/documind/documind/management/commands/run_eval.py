import json
from pathlib import Path
from django.core.management.base import BaseCommand
from documind.retrieval import query_handbook

class Command(BaseCommand):
    help = 'Run evaluation suite on 20 test questions and record exact score'

    def handle(self, *args, **options):
        eval_path = Path(__file__).resolve().parent.parent.parent.parent / 'eval' / 'questions.json'

        with open(eval_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)

        total = len(questions)
        correct = 0
        misses = []

        self.stdout.write(f"Running DocuMind evaluation on {total} questions...")

        for q in questions:
            res = query_handbook(q['question'])
            if q['should_find']:
                # Pass if status is found and page matches expected page
                if res['status'] == 'found' and res['source_page'] == q['expected_page']:
                    correct += 1
                else:
                    misses.append({
                        "id": q['id'],
                        "question": q['question'],
                        "expected_page": q['expected_page'],
                        "actual_status": res['status'],
                        "actual_page": res['source_page']
                    })
            else:
                # Should not find (unanswerable questions) -> status must be not_found
                if res['status'] == 'not_found':
                    correct += 1
                else:
                    misses.append({
                        "id": q['id'],
                        "question": q['question'],
                        "expected": "not_found",
                        "actual": f"Hallucinated or matched page {res['source_page']}"
                    })

        self.stdout.write(self.style.SUCCESS(f"\nEvaluation Complete: {correct} of {total} questions answered correctly."))
        if misses:
            self.stdout.write(self.style.WARNING(f"Misses ({len(misses)}):"))
            for m in misses:
                self.stdout.write(f"  - #{m['id']} '{m['question']}': {m}")
        else:
            self.stdout.write("Zero misses recorded.")
