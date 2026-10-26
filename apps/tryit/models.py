from django.db import models


class TryBooking(models.Model):
    """
    A booking made on the BookIt Try it page (sample venue).
    The unique constraint is what stops double bookings: if two people book the same slot at the
    same moment, the database accepts only one of them.
    Bookings for past dates are deleted automatically (see apps/tryit/booking.py).
    """
    date = models.DateField()
    resource = models.CharField(max_length=40)
    start_hour = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'resource', 'start_hour'], name='one_booking_per_slot'),
        ]
        ordering = ['date', 'start_hour']

    def __str__(self):
        return f'{self.date} {self.start_hour:02d}:00 {self.resource}'


class AiUsage(models.Model):
    """
    How many AI calls the whole site made on one day (UTC). Used for the daily cap (AI_DAILY_CAP) that protects
    the API keys and bills. Kept in the database so every server process shares the same count.
    """
    day = models.DateField(unique=True)
    calls = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-day']
        verbose_name = 'AI usage (per day)'
        verbose_name_plural = 'AI usage (per day)'

    def __str__(self):
        return f'{self.day}: {self.calls} AI calls'
