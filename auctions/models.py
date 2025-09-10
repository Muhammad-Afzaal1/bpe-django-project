from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

 
class Listing(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=1000)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(blank=True)
    date_time = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
    


# class Bid(models.Model):
#     pass

# class Comment(models.Model):
#     pass