from django import forms
from .models import Listing, Bid, Review

class ListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "listing_type",
            "starting_bid",
            "buy_now_price",
            "stock",
            "image",
            "category"
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "listing_type": forms.Select(attrs={"class": "form-select"}),
            "starting_bid": forms.NumberInput(attrs={"class": "form-control"}),
            "buy_now_price": forms.NumberInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.URLInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get("listing_type")
        starting_bid = cleaned_data.get("starting_bid")
        buy_now_price = cleaned_data.get("buy_now_price")
        stock = cleaned_data.get('stock')

        if(stock <=0):
            self.add_error('stock', "Stock should be greater than 0.")
        if listing_type == Listing.AUCTION and not starting_bid:
            self.add_error("starting_bid", "Starting bid is required for auction listings.")

        if listing_type == Listing.BUY_NOW and not buy_now_price:
            self.add_error("buy_now_price", "Buy now price is required.")

        return cleaned_data

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS0JPlBPWAJmuK_QMJjXiY8AlthB5ZinSaJ9Q&s"
        return image

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Write your feedback (optional)"
            }),
        }
