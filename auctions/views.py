from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from .models import User, Listing, LISTING_CATEGORIES, Bid, Comment, Replies


class CreateListing (forms.Form):
    model = Listing
    title = forms.CharField(max_length=30, label="Title*", label_suffix="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter the product title', 'autofocus': 'autofocus'}))
    price = forms.DecimalField(decimal_places=2, label="Starting Bid*", label_suffix="",
                               widget=forms.NumberInput(attrs={'placeholder': 'Enter initial Bid'}), min_value=1, max_value=999999999)
    image = forms.URLField(required=False, label="Image URL", label_suffix="",
                           widget=forms.TextInput(attrs={'placeholder': 'Enter image URL'}))
    category = forms.ChoiceField(choices=LISTING_CATEGORIES, label_suffix="")
    description = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Enter product description '}), label="Description*", label_suffix="")


class categoryForm(forms.Form):
    category = forms.ChoiceField(choices=LISTING_CATEGORIES)
    category.widget.attrs.update(
        {'class': 'selector', 'onchange': 'this.form.submit()'})


class commentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control", "cols": "30", "rows": "3"}))


def handler404(request, *args, **kwargs):
    return HttpResponseRedirect(f"/Error404/UnknownPath")


def Error404(request):
    return render(request, "auctions/PageNotFound.html")


def re_path(request):
    return HttpResponseRedirect(f"/activeListings")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                messages.success(
                    request, f"Successfully Logged in as {username} <br> Create a new listing below")
                return HttpResponseRedirect(request.POST.get('next'))
            else:
                messages.success(
                    request, f"Successfully Logged in as {username}")
                return HttpResponseRedirect('/')
        else:
            messages.error(
                request, "Invalid username and/or password <br> Note that both fields may be case-sensitive")
            return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return HttpResponseRedirect('/')


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords doesn't match"
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken"
            })
        login(request, user)
        messages.success(
            request, f"Successfully registered as {username} <br> Check in email for confirmation")
        return HttpResponseRedirect(reverse("index", args=('activeListings',)))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        form = CreateListing(request.POST)
        if form.is_valid() and (form.cleaned_data["category"] != "ALL"):
            title = (form.cleaned_data["title"]).strip()
            description = (form.cleaned_data["description"]).strip()
            price = form.cleaned_data["price"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            listing = Listing(creator=request.user, title=title,
                              description=description, price=price, image=image, category=category)
            bid = Bid(listing=listing, bidder=request.user, bid_price=price)
            listing.save()
            bid.save()
            messages.success(
                request, f"Created a listing named \"{title}\" successfully")
            return HttpResponseRedirect(reverse("index", args=('activeListings',)))
        elif form.is_valid():
            messages.error(request, f"Catagory should not be left empty")
            return render(request, "auctions/create.html", {
                "listing_form": form
            })
        else:
            messages.error(
                request, f"Error occured while translating image URL")
            return render(request, "auctions/create.html", {
                "listing_form": form
            })
    return render(request, "auctions/create.html", {
        "listing_form": CreateListing()
    })


def bidaction(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        bid_price = request.POST["bidding_price"]
        bid = Bid(listing=listing, bidder=request.user, bid_price=bid_price)
        bid.save()
        messages.success(
            request, f"We have recieved your bid at ${bid_price} successfully")
    else:
        listing.active = False
        if listing.bids.all().count() < 2:
            messages.success(request, f"The auction was closed with 0 Bids")
        else:
            listing.winner = listing.get_highestbid()[0].bidder
            messages.success(
                request, f"The auction was closed successfully with {listing.winner} as the winner")
        listing.save()

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required
def watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if listing in request.user.watchlist.all():
        request.user.watchlist.remove(listing)
        messages.success(request, "Successfully removed from your watchlist")
    else:
        request.user.watchlist.add(listing)
        messages.success(request, "Successfully added to your watchlist")
    return HttpResponseRedirect(f"/listing/{listing.id}")


def category(request, listing_name):
    if request.method == "POST":
        form = categoryForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data["category"]
            if value == "ALL":
                return HttpResponseRedirect(reverse("index", args=('activeListings',)))
            listings, stat = None, None
            if listing_name == "activeListings":
                listings = Listing.objects.filter(active=True, category=value)
                stat = "Active Listings"
            elif listing_name == "allListings":
                listings = Listing.objects.filter(category=value)
                stat = "All Listings"
            elif listing_name == "myWatchlist" and request.user.is_authenticated:
                listings = request.user.watchlist.filter(category=value)
                stat = "My Watchlist"
            elif listing_name == "myListings" and request.user.is_authenticated:
                listings = request.user.listings.filter(category=value)
                stat = "My Listings"

            if listings is not None:
                return render(request, "auctions/index.html", {
                    "listings": listings,
                    "stat": (stat, listing_name),
                    "options": form
                })
            else:
                return HttpResponseRedirect(reverse("index", args=('activeListings',)))
        else:
            return HttpResponseRedirect(reverse("index", args=('activeListings',)))
    return HttpResponseRedirect(f"/Error404/UnknownPath")


def index(request, listing_name):
    listings, stat = None, None
    if listing_name == "activeListings":
        listings = Listing.objects.filter(active=True)
        stat = "Active Listings"
    elif listing_name == "allListings":
        listings = Listing.objects.all()
        stat = "All Listings"
    elif listing_name == "myWatchlist" and request.user.is_authenticated:
        listings = request.user.watchlist.all()
        stat = "My Watchlist"
    elif listing_name == "myListings" and request.user.is_authenticated:
        listings = request.user.listings.all()
        stat = "My Listings"

    if listings is not None:
        return render(request, "auctions/index.html", {
            "listings": listings,
            "stat": (stat, listing_name),
            "options": categoryForm()
        })
    else:
        return HttpResponseRedirect(f"/Error404/UnknownPath")


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.user.is_authenticated:
        biduser = Bid.objects.filter(listing=listing, bidder=request.user)
    else:
        biduser = None
    comments = Comment.objects.filter(listing=listing)
    tcoms = 0
    for comment in comments:
        tcoms += comment.reply.all().count() + 1

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "highest_bid": listing.get_highestbid()[0],
        "biduser": biduser,
        "commentForm": commentForm(),
        "comments": comments,
        "totalcomments": tcoms
    })


@login_required
def comment(request, listing_id):
    if request.method == "POST":
        form = commentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            listing = Listing.objects.get(pk=listing_id)
            c = Comment(listing=listing,
                        commenter=request.user, content=content)
            c.save()
        messages.success(
            request, f"Successfully replied to a post named \"{listing.title}\"")
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required
def reply(request, listing_id, comment_id):
    print(request.GET)
    String = "r"+str(comment_id)
    content = request.GET.get(String)
    comment = Comment.objects.get(pk=comment_id)
    replies = Replies(commenter=request.user, comment=comment, content=content)
    replies.save()
    messages.success(request, f"Successfully replied to a Comment")
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
