from django import forms
from .models import Listing, Bid, Comment

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "image", "starting_bid", "category"]

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return "https://png.pngtree.com/png-vector/20221125/ourmid/pngtree-no-image-available-icon-flatvector-illustration-thumbnail-graphic-illustration-vector-png-image_40966590.jpg"
        return image
    
class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]