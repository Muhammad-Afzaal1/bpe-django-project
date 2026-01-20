from django import forms
from .models import Listing, Bid, Comment

class ListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "listing_type",
            "starting_bid",
            "buy_now_price",
            "image",
            "category"
        ]

    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get("listing_type")
        starting_bid = cleaned_data.get("starting_bid")
        buy_now_price = cleaned_data.get("buy_now_price")

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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4})
        }