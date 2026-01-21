from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q, Max
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import ListingForm, BidForm, ReviewForm
from .models import User, Listing, Category, Comment, Watchlist, Order, Review, Bid


def index(request):
    listings = Listing.objects.filter(active=True)

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
    review_form = ReviewForm()
    comments = Comment.objects.filter(listing = listing)
    in_watchlist = False
    watchlist_items = 0
    if request.user.is_authenticated:
        in_watchlist = listing.watchlist_set.filter(user = request.user).exists()
        watchlist_items = Listing.objects.filter(watchlist__user = request.user).count()
    reviews = listing.reviews.all()
    return render(request, "auctions/listing.html",{
        "listing":listing,
        "form":form,
        "review_form":review_form,
        "comments":comments,
        "reviews": reviews,
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

    if listing.stock <= 0:
        messages.error(request, "This item is out of stock.")
        return redirect("listing", listing_id)

    

    if listing.stock == 0:
        listing.active = False

    listing.save()

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

    try:
        quantity = int(request.POST.get("quantity", 1))
        if(quantity > listing.stock):
            messages.error(request, "Invalid quantity.")
            return redirect("listing", listing_id)
    except ValueError:
        messages.error(request, "Invalid quantity.")
        return redirect("listing", listing_id)
    
    # ✅ Perform purchase (basic version)
    Order.objects.create(
        buyer=request.user,
        listing=listing,
        price=listing.buy_now_price,
        quantity = quantity
    )
    listing.stock-=quantity
    if listing.stock == 0:
        listing.active = False
    listing.save()

    messages.success(
        request,
        f"You successfully purchased '{listing.title}' for ${listing.buy_now_price}."
    )

    return redirect("listing", listing_id)

@login_required
def add_review(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    has_order = Order.objects.filter(
        buyer=request.user,
        listing=listing
    ).exists()

    # Check if user won the auction
    is_winner = False
    if not listing.active and listing.listing_type == Listing.AUCTION:
        highest_bid = listing.highest_bid()
        if highest_bid and highest_bid.bidder == request.user:
            is_winner = True

    if not has_order and not is_winner:
        messages.error(request, "You can only review items you purchased or won.")
        return redirect("listing", listing_id)

    if Review.objects.filter(user=request.user, listing=listing).exists():
        messages.error(request, "You already reviewed this item.")
        return redirect("listing", listing_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.listing = listing
            review.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect("listing", listing_id)

@login_required
def purchased_items(request):
    # 1. Direct Orders
    orders = request.user.orders.select_related('listing').order_by("-created_at")

    # 2. Won Auctions
    # Get all inactive auction listings where the user placed a bid
    # Then filter in Python to find ones where they are the highest bidder
    
    # Optimization: Filter listings that are closed, are auctions, and user bid on them
    candidates = Listing.objects.filter(
        active=False, 
        listing_type=Listing.AUCTION,
        bids__bidder=request.user
    ).distinct()

    won_auctions = []
    for listing in candidates:
        highest = listing.highest_bid()
        if highest and highest.bidder == request.user:
            won_auctions.append(listing)

    # Calculate count for watchlist (sidebar/header usually needs it)
    watchlist_count = Listing.objects.filter(watchlist__user=request.user).count()

    return render(request, "auctions/purchased.html", {
        "orders": orders,
        "won_auctions": won_auctions,
        "count": watchlist_count,
        "categories": Category.objects.all()
    })

@login_required
def auctioned_listings(request):
    # 1. Active Bids
    # Listings that are active, are auctions, and user has bid on them
    active_bids_listings = Listing.objects.filter(
        active=True,
        listing_type=Listing.AUCTION,
        bids__bidder=request.user
    ).distinct()

    active_bids = []
    for listing in active_bids_listings:
        # Get user's max bid on this listing
        user_max_bid = listing.bids.filter(bidder=request.user).aggregate(Max('amount'))['amount__max']
        listing.user_max_bid = user_max_bid
        active_bids.append(listing)

    # 2. Lost Auctions
    # Listings that are closed, are auctions, user bid on them, but user is NOT the winner
    lost_candidates = Listing.objects.filter(
        active=False,
        listing_type=Listing.AUCTION,
        bids__bidder=request.user
    ).distinct()

    lost_auctions = []
    for listing in lost_candidates:
        highest = listing.highest_bid()
        # If there is a winner and it is NOT the current user
        if highest and highest.bidder != request.user:
            # Get user's max bid
            user_max_bid = listing.bids.filter(bidder=request.user).aggregate(Max('amount'))['amount__max']
            listing.user_max_bid = user_max_bid
            lost_auctions.append(listing)

    watchlist_count = Listing.objects.filter(watchlist__user=request.user).count()

    return render(request, "auctions/auctioned_listings.html", {
        "active_bids": active_bids,
        "lost_auctions": lost_auctions,
        "count": watchlist_count,
        "categories": Category.objects.all()
    })

@login_required
def seller_dashboard(request):
    if not request.user.is_seller():
        return HttpResponseForbidden("Only registered sellers can view this dashboard.")

    # Get all listings created by this user, ordered by date
    my_listings = Listing.objects.filter(creator=request.user).order_by("-date_time")
    
    watchlist_count = Listing.objects.filter(watchlist__user=request.user).count()

    return render(request, "auctions/seller_dashboard.html", {
        "listings": my_listings,
        "count": watchlist_count,
        "categories": Category.objects.all()
    })

@login_required
def update_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    # Ensure user is the creator
    if listing.creator != request.user:
        return HttpResponseForbidden("You do not have permission to modify this listing.")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "toggle_status":
            # Toggle active status
            listing.active = not listing.active
            listing.save()
            status_msg = "activated" if listing.active else "deactivated"
            messages.success(request, f"Listing '{listing.title}' has been {status_msg}.")

        elif action == "update_stock":
             # Update stock quantity (Buy Now only)
            if listing.listing_type == Listing.BUY_NOW:
                try:
                    new_stock = int(request.POST.get("stock", 0))
                    if new_stock < 0:
                         messages.error(request, "Stock cannot be negative.")
                    else:
                        listing.stock = new_stock
                        listing.save()
                        messages.success(request, f"Stock updated for '{listing.title}'.")
                except ValueError:
                    messages.error(request, "Invalid stock value.")

        else:
            messages.error(request, "Invalid action.")

    # Redirect back to where they came from (dashboard or listing page)
    return redirect(request.META.get('HTTP_REFERER', 'seller_dashboard'))