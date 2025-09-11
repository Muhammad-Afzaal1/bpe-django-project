from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import ListingForm, BidForm
from .models import User, Listing, Category


def index(request):
    listings = Listing.objects.all()

    return render(request, "auctions/index.html",{
        "listings":listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            form.save()
            messages.success(request, "Listing has been created successfully")
            return redirect("create_listing")
        else:
            messages.error(request, "Please correct the error below")
    else:
        form = ListingForm()

    return render(request, "auctions/create_listing.html", {
        "form":form
    })

def listing(request, id):
    listing = get_object_or_404(Listing, pk=id)
    form = BidForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged In to place bid")
            return redirect('login')
        form = BidForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data["amount"]
            if bid_amount < listing.starting_bid:
                messages.error(request, "Your bid must be greater than the Starting Bid")
            elif bid_amount < listing.current_price:
                messages.error(request, "Your bid must be grater than current Highest Bid")
            else:
                bid = form.save(commit = False)
                bid.bidder = request.user
                bid.listing = listing
                bid.save()
                messages.success(request, "your bid was placed successfully.")
                return redirect("listing", id=listing.id)
    return render(request, "auctions/listing.html",{
        "listing":listing,
        "form":form
    })

def close_listing(request, id):
    listing = get_object_or_404(Listing, pk = id)
    if not request.user == listing.creator:
        messages.error("You don't have permissions to close the listing")
        return redirect("listing", id = id)
    
    listing.active = False
    listing.save()
    return redirect("listing", id = id)