from django.urls import path

from . import views

urlpatterns = [
    path("",views.re_path),
    path("Error404/UnknownPath",views.Error404,name="Error"),
    path("<str:listing_name>", views.index, name="index"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout", views.logout_view, name="logout"),
    path("accounts/register", views.register, name="register"),
    path("accounts/listing/create",views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/<int:listing_id>/watchlist", views.watchlist, name = "watchlist"),
    path("<str:listing_name>/category", views.category, name="category"),
    path("listing/<int:listing_id>/bidding", views.bidaction, name="bid"),
    path("listing/<int:listing_id>/comment", views.comment, name="comment"),
    path("listing/<int:listing_id>/reply/<int:comment_id>", views.reply, name="reply")
]
