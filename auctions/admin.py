from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import User, Listing, Bid, Comment, Replies

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "creator", "title", "timestamp", "price", "category", "active", "winner")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "commenter", "timestamp", "content")

class RepliesAdmin(admin.ModelAdmin):
    list_display = ("id","comment","commenter", "content", "timestamp")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "bidder", "timestamp", "bid_price")

class CustomUserAdmin(UserAdmin):
    filter_horizontal = ("watchlist",)
    fieldsets = UserAdmin.fieldsets + (
        ("Watchlist", {'fields': ('watchlist',)}),
    )

# Register your models here.
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Replies, RepliesAdmin)