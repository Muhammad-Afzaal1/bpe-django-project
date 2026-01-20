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
    path("listings/<int:id>/add-comment", views.add_comment, name="add_comment"),
    path("listings/<int:id>/watchlist", views.toggle_watchlist, name="toggle_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name='categories'),
    path("categories/<str:category>", views.category, name="category"),
    path("become-seller/", views.become_seller, name="become_seller"),
]
