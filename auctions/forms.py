from django import forms
from .models import Listing, Bid, Comment

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "image", "starting_bid", "category"]

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