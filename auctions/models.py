from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    BUYER = "buyer"
    SELLER = "seller"

    ROLE_CHOICES = [
        (BUYER, "Buyer"),
        (SELLER, "Seller"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=BUYER
    )

    def is_seller(self):
        return self.role == self.SELLER

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

 
class Listing(models.Model):

    AUCTION = "auction"
    BUY_NOW = "buy_now"

    LISTING_TYPE_CHOICES = [
        (AUCTION, "Auction"),
        (BUY_NOW, "Buy Now"),
    ]

    title = models.CharField(max_length=150)
    description = models.CharField(max_length=1000)

    listing_type = models.CharField(
        max_length=10,
        choices=LISTING_TYPE_CHOICES,
        default=AUCTION
    )

    starting_bid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    buy_now_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    image = models.URLField(max_length=400, blank=True)
    date_time = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=1)

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None


    def __str__(self):
        return self.title
    
    def highest_bid(self):
        return self.bids.order_by("-amount").first()
    
    @property
    def current_price(self):
        if self.listing_type == self.BUY_NOW:
            return self.buy_now_price
        return self.highest_bid().amount if self.highest_bid() else self.starting_bid

    


class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"${self.amount} by {self.bidder.username} on {self.listing.title}"

class Comment (models.Model):
    comment = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.comment} from {self.user} for {self.listing}"
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'listing')


    def __str__(self):
        return f"{self.user.username} -> {self.listing.title}"
    

class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return f"{self.buyer} bought {self.listing}"
    
class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "listing")

    def __str__(self):
        return f"{self.rating}⭐ by {self.user}"
