from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max
from django.utils import timezone
from datetime import datetime
import decimal
import calendar
LISTING_CATEGORIES = (
    ('ALL', 'Choose...'),
    ('BOOKS', 'Books'),
    ('MUSIC', 'Music'),
    ('MOVIES', 'Movies'),
    ('GAMES', 'Games'),
    ('COMPUTERS', 'Computers'),
    ('ELECTRONICS', 'Electronics'),
    ('KITCHEN', 'Kitchen'),
    ('HOME', 'Home'),
    ('HEALTH', 'Health'),
    ('PETS', 'Pets'),
    ('TOYS', 'Toys'),
    ('FASHION', 'Fashion'),
    ('SHOES', 'Shoes'),
    ('SPORTS', 'Sports'),
    ('BABY', 'Baby'),
    ('TRAVEL', 'Travel')
)

def td_format(td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ('year',        60*60*24*365),
            ('month',       60*60*24*30),
            ('day',         60*60*24),
            ('hour',        60*60),
            ('minute',      60),
            ('second',      1)
        ]

        strings = []
        for period_name, period_seconds in periods:
            if seconds >= period_seconds:
                period_value, seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append("%s %s%s" % (period_value, period_name, has_s))
                break

        return ", ".join(strings)

class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "Listing", blank=True, related_name="watchlist")


class Listing(models.Model):
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings", null=True)
    title = models.CharField(max_length=200, verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(
        decimal_places=2, verbose_name="Starting Bid", max_digits=10)
    image = models.URLField(blank=True, verbose_name="Image URL", null=True)
    category = models.CharField(choices=LISTING_CATEGORIES, blank=True,
                                verbose_name="Category", max_length=200, null=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def date_time(self):
        date_time = (str(self.timestamp)).split(" ")
        mydate = datetime.strptime(date_time[0],'%Y-%m-%d')
        return f"{(calendar.day_abbr[self.timestamp.weekday()])}, {calendar.month_abbr[mydate.month]} {mydate.day} {mydate.year}"
        # return f"{self.timestamp.weekday()} {date_time[0][2]} {date_time[1][1]} {date_time[2][3]} "

    def __str__(self):
        return self.title
    
    def get_user_bids(self,request):
        t= request.user.bids.filter(listing = self)
        return t

    def get_highestbid(self):
        t = Bid.objects.filter(listing=self).order_by("bid_price").reverse()
        return t


class Bid(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids", null=True)
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids", null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    bid_price = models.DecimalField(
        decimal_places=2, verbose_name="Bid Price", max_digits=15, null=True)

    def date(self):
        return td_format(timezone.now() - self.timestamp)
    
    def __str__(self):
        return f"{self.bidder} bid ${self.bid_price} for {self.listing}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", null=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", null=True)
    content = models.TextField(verbose_name="Comment", default="")
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def date_time(self):
        return td_format(timezone.now() - self.timestamp)

    def __str__(self):
        return f"{self.commenter} commented on {self.listing} ({self.timestamp.date()})"

class Replies(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reply", null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reply", null = True)
    content = models.TextField(verbose_name="Replies", default="", null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    
    def date_time(self):
        return td_format(timezone.now() - self.timestamp)
        
    def __str__(self):
        return f"{self.commenter} replied to {self.comment} ({self.timestamp.date()})"