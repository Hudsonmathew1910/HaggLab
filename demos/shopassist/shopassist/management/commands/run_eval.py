import json
from pathlib import Path
from django.core.management.base import BaseCommand
from shopassist.agent import process_shopper_message

class Command(BaseCommand):
    help = 'Run evaluation suite on shopper queries and record exact score'

    def handle(self, *args, **options):
        eval_path = Path(__file__).resolve().parent.parent.parent.parent / 'eval' / 'conversations.json'
        with open(eval_path, 'r', encoding='utf-8') as f:
            conversations = json.load(f)

        total = len(conversations)
        correct = 0
        misses = []

        self.stdout.write(f"Running ShopAssist evaluation on {total} conversation scenarios...")

        for c in conversations:
            res = process_shopper_message(c['user_message'])
            products = res['products']
            if c['should_find']:
                # Success if products found and category matches
                if len(products) > 0:
                    first_cat = products[0]['category']
                    if first_cat.lower() == c['expected_category'].lower():
                        correct += 1
                    else:
                        misses.append({
                            "id": c['id'],
                            "message": c['user_message'],
                            "expected_category": c['expected_category'],
                            "actual_category": first_cat
                        })
                else:
                    misses.append({
                        "id": c['id'],
                        "message": c['user_message'],
                        "expected": "products found",
                        "actual": "0 products"
                    })
            else:
                # Should find 0 products for out-of-scope queries
                if len(products) == 0:
                    correct += 1
                else:
                    misses.append({
                        "id": c['id'],
                        "message": c['user_message'],
                        "expected": "0 products",
                        "actual": f"{len(products)} products matched"
                    })

        self.stdout.write(self.style.SUCCESS(f"\nEvaluation Complete: {correct} of {total} scenarios answered correctly."))
        if misses:
            self.stdout.write(self.style.WARNING(f"Misses ({len(misses)}):"))
            for m in misses:
                self.stdout.write(f"  - #{m['id']} '{m['message']}': {m}")
        else:
            self.stdout.write("Zero misses recorded.")
