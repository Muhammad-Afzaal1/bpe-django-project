from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import ListingForm, BidForm, CommentForm
from .models import User, Listing, Category, Comment, Watchlist


def index(request):
    listings = Listing.objects.filter(active = True)

    query = request.GET.get('q')
    category_id = request.GET.get('category')
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if query:
        listings = listings.filter(
            Q(title__icontains=query),
            Q(description__icontains=query)
        )

    if category_id:
        listings = listings.filter(category_id=category_id)

    if min_price:
        listings = listings.filter(starting_bid__gte=min_price)

    if max_price:
        listings = listings.filter(starting_bid__lte=max_price)

    if request.user.is_authenticated:
        watchlist_count = request.user.watchlist_set.all()
        return render(request, "auctions/index.html",{
            "listings":listings,
            "count":len(watchlist_count),
            "categories":Category.objects.all()
        })
    else:
        return render(request, "auctions/index.html",{
            "listings":listings,
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
        if not username or not email or not password or not confirmation:
            return render(request, "auctions/register.html", {
                "message": "All fields are required."
            })
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
    if not request.user.is_seller():
        return HttpResponseForbidden("Only seller can create listing")
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
        watchlist_items = Listing.objects.filter(watchlist__user = request.user)

    return render(request, "auctions/create_listing.html", {
        "form":form,
        "count":watchlist_items.count()
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
    comment_form = CommentForm()
    comments = Comment.objects.filter(listing = listing)
    in_watchlist = False
    watchlist_items = 0
    if request.user.is_authenticated:
        in_watchlist = listing.watchlist_set.filter(user = request.user).exists()
        watchlist_items = Listing.objects.filter(watchlist__user = request.user).count()
    return render(request, "auctions/listing.html",{
        "listing":listing,
        "form":form,
        "comment_form":comment_form,
        "comments":comments,
        "in_watchlist":in_watchlist,
        "count":watchlist_items
    })

def close_listing(request, id):
    listing = get_object_or_404(Listing, pk = id)
    if not request.user == listing.creator:
        messages.error("You don't have permissions to close the listing")
        return redirect("listing", id = id)
    
    listing.active = False
    listing.save()
    return redirect("listing", id = id)

@login_required
def add_comment(request, id):
    listing = get_object_or_404(Listing, pk = id)
    comment = CommentForm(request.POST)
    comment = comment.save(commit=False)
    comment.user = request.user
    comment.listing = listing
    comment.save()

    return redirect("listing", id=id)

@login_required
def toggle_watchlist(request, id):
    listing = get_object_or_404(Listing, pk = id)
    watchlist_item = Watchlist.objects.filter(listing = listing, user = request.user).first()

    if watchlist_item:
        watchlist_item.delete()
    else:
        Watchlist.objects.create(user = request.user, listing = listing)

    return redirect('listing', id = id)

@login_required
def watchlist(request):
    watchlist_items = request.user.watchlist_set.all()
    listings = [item.listing for item in watchlist_items]
    return render(request, "auctions/index.html", {
        "listings":listings,
        "count": len(listings),
        "categories":Category.objects.all()
    })

def categories(request):
    categories = Category.objects.all()
    watchlist_items = 0
    if request.user.is_authenticated:
        watchlist_items = Listing.objects.filter(watchlist__user = request.user).count()
    return render(request, "auctions/categories.html",{
        "categories":categories,
        "count": watchlist_items
    })

def category(request, category):
    category = get_object_or_404(Category, name = category)
    listings = Listing.objects.filter(category = category, active = True)
    watchlist_items = 0
    if request.user.is_authenticated:
        watchlist_items = Listing.objects.filter(watchlist__user = request.user).count()
    return render(request, "auctions/index.html",{
        "listings":listings,
        "count": watchlist_items
    })


@login_required
def become_seller(request):
    if request.method == "POST":
        if request.user.role == "seller":
            return HttpResponseForbidden("You are already a seller.")

        request.user.role = "seller"
        request.user.save()

        return redirect("index")

    return HttpResponseForbidden("Invalid request.")

@login_required
def buy_now(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    # Only POST allowed
    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect("listing", listing_id)

    # Must be Buy Now listing
    if listing.listing_type != Listing.BUY_NOW:
        messages.error(request, "This item is not available for direct purchase.")
        return redirect("listing", listing_id)

    # Listing must be active
    if not listing.active:
        messages.error(request, "This listing is no longer active.")
        return redirect("listing", listing_id)

    # Seller cannot buy own item
    if listing.creator == request.user:
        messages.error(request, "You cannot buy your own listing.")
        return redirect("listing", listing_id)

    # ✅ Perform purchase (basic version)
    listing.active = False
    listing.save()

    messages.success(
        request,
        f"You successfully purchased '{listing.title}' for ${listing.buy_now_price}."
    )

    return redirect("listing", listing_id)
