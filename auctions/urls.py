from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.create_listing, name="create_listing"),
    path("listings/<int:id>", views.listing, name="listing",),
    path("listings/<int:id>/close", views.close_listing, name="close_listing"),
    path("listings/<int:listing_id>/add-review", views.add_review, name="add_review"),
    path("listings/<int:id>/watchlist", views.toggle_watchlist, name="toggle_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("purchased", views.purchased_items, name="purchased_items"),
    path("auctioned", views.auctioned_listings, name="auctioned_listings"),
    path("categories", views.categories, name='categories'),
    path("categories/<str:category>", views.category, name="category"),
    path("become-seller/", views.become_seller, name="become_seller"),
    path("buy-now/<int:listing_id>/", views.buy_now, name="buy_now"),
    path("selling", views.seller_dashboard, name="seller_dashboard"),
    path("listings/<int:listing_id>/update", views.update_listing, name="update_listing"),
    path("orders/<int:order_id>/process", views.process_order, name="process_order"),
    path("orders/<int:order_id>/cancel", views.cancel_order, name="cancel_order"),
    path("orders/<int:order_id>/complete", views.complete_order, name="complete_order"),
]

