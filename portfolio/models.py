from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxLengthValidator

class Trade(models.Model):
    ACTIONS = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trades',
    )

    symbol = models.CharField(
        max_length=10,
        validators=[MaxLengthValidator(10)],
        help_text="Stock ticker symbol, e.g., AAPL"
    )
    action = models.CharField(
        max_length=4,
        choices=ACTIONS,
        help_text="Type of trade: BUY or SELL"
    )
    shares = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of shares (must be >= 1)"
    )
    price = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Price per share in USD"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the trade was executed"
    )

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} | {self.action} {self.shares} {self.symbol} @ ${self.price:.2f}"

    class Meta:
        ordering = ['-timestamp']


class PortfolioEntry(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='portfolio_entries',
    )
    symbol = models.CharField(
        max_length=10,
        unique=True,
        validators=[MaxLengthValidator(10)],
        help_text="Stock ticker symbol, must be unique per user"
    )
    shares = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Current number of shares owned"
    )
    average_price = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Average price per share (USD)"
    )

    def __str__(self):
        return f"{self.symbol}: {self.shares} shares @ ${self.average_price:.2f}"
