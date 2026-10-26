"""
BookIt: free slots and bookings for Green Field Sports Arena (sample venue, see datasets/bookit/venue_rules.md).

No AI is needed: availability is calculated, and the database refuses a second booking for the same slot.
To make the sample venue look realistic, some slots are already taken by other (simulated) players.
The pattern is fixed per date and slot, and busier in the evening and at weekends, like the history in bookings.csv.
"""
import hashlib
from datetime import date, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import TryBooking

RESOURCES = {
    'turf-a': ('Turf A (5-a-side)', 60.0),
    'turf-b': ('Turf B (5-a-side)', 60.0),
    'turf-c': ('Turf C (7-a-side)', 90.0),
    'badminton-1': ('Badminton Court 1', 15.0),
    'badminton-2': ('Badminton Court 2', 15.0),
}
FIRST_HOUR, LAST_HOUR = 6, 22  # last booking starts at 22:00
BOOK_AHEAD_DAYS = 14


class BookingError(ValueError):
    """A visitor-facing booking problem."""


def is_peak(day, hour):
    return day.weekday() >= 5 or hour >= 17


def price(resource, day, hour):
    base = RESOURCES[resource][1]
    return round(base * 1.3, 2) if is_peak(day, hour) else base


def simulated_taken(resource, day, hour):
    """Stable pseudo-random occupancy by other players."""
    busy = 0.2 + (0.4 if hour >= 17 else 0) + (0.2 if day.weekday() >= 5 else 0)
    busy *= max(0.25, 1 - (day - timezone.localdate()).days / 18)  # later dates are emptier
    digest = hashlib.sha256(f'{resource}|{day}|{hour}'.encode()).digest()
    return digest[0] / 255 < busy


def check_date(value):
    day = date.fromisoformat(value)
    today = timezone.localdate()
    if day < today:
        raise BookingError('Please pick today or a later date.')
    if day > today + timedelta(days=BOOK_AHEAD_DAYS):
        raise BookingError(f'Bookings open {BOOK_AHEAD_DAYS} days in advance. Please pick an earlier date.')
    return day


def clean_old():
    old = TryBooking.objects.filter(date__lt=timezone.localdate())
    if old.exists():  # read first, so most requests never need a write lock
        old.delete()


def free_slots(resource, day):
    if resource not in RESOURCES:
        raise BookingError('Please pick a court.')
    clean_old()
    booked = set(TryBooking.objects.filter(date=day, resource=resource).values_list('start_hour', flat=True))
    now = timezone.localtime()
    items = []
    for hour in range(FIRST_HOUR, LAST_HOUR + 1):
        if day == now.date() and hour <= now.hour:
            continue
        if hour in booked or simulated_taken(resource, day, hour):
            continue
        items.append({'slot': f'{hour:02d}:00', 'title': f'{hour:02d}:00 - {hour + 1:02d}:00',
                      'meta': f"{'Peak' if is_peak(day, hour) else 'Off-peak'} · {price(resource, day, hour):.2f}"})
    return items


def slots_reply(resource, day):
    items = free_slots(resource, day)
    name = RESOURCES[resource][0]
    if not items:
        return {'text': f'{name} is fully booked on {day:%A %d %B}. Try another court or date.'}
    return {'text': f'{len(items)} free slots for {name} on {day:%A %d %B}. Pick one, add your name, then book.',
            'items': items}


def book(resource, day, slot, name):
    if not name:
        raise BookingError('Please add your name to book.')
    try:
        hour = int(slot.split(':')[0])
    except (ValueError, AttributeError):
        raise BookingError('Please pick a slot first.')
    if slot not in {i['slot'] for i in free_slots(resource, day)}:
        raise BookingError('Sorry, that slot was just taken. Please pick another one.')
    try:
        with transaction.atomic():
            TryBooking.objects.create(date=day, resource=resource, start_hour=hour, name=name[:80])
    except IntegrityError:
        raise BookingError('Sorry, that slot was just taken. Please pick another one.')
    label = RESOURCES[resource][0]
    return {
        'text': f'Booked! {label}, {day:%A %d %B}, {slot} to {hour + 1:02d}:00, for {name}. '
                'In the real system you would now get a confirmation email with a QR code for check-in.',
        'labels': ['Confirmed', f'Price {price(resource, day, hour):.2f}'],
        'source': 'Green Field Sports Arena (sample venue). Sample bookings are removed after their date.',
    }


def run(payload):
    resource = payload.get('resource', 'turf-a')
    day = check_date(payload.get('date') or timezone.localdate().isoformat())
    if payload.get('action') == 'book':
        return book(resource, day, payload.get('slot', ''), payload.get('name', ''))
    return slots_reply(resource, day)
