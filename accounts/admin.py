from django.contrib import admin
from .models import Account, UsersReferralPercentage, UsersBankDetail, UserBalance,HotGame,ShowcaseSlider,PremierLeagueGame,Package,FootballMatch,Match,BetHistory,DepositRequest, WithdrawalRequest,AdminBankAccount,PurchasePackage,soccer_slider,ReferralBonus,leagues_slider
from django.utils.html import format_html
from django.urls import reverse


class AccountAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'username', 'fullname','is_active', 'is_staff', 'date_joined')
    search_fields = ('phone', 'email', 'username')
    list_filter = ('is_active', 'is_staff', 'is_superuser')

class UsersReferralPercentageAdmin(admin.ModelAdmin):
    list_display = ('percentage',)
    search_fields = ('percentage',)

class UsersBankDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'bank_name', 'account_holder_name')
    search_fields = ('user__phone', 'account_number', 'bank_name', 'account_holder_name')

class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'main_balance', 'total_profits', 'purchased_package_name', 'purchased_package')
    search_fields = ('user__username', 'user__phone', 'purchased_package_name')


@admin.register(HotGame)
class HotGameAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'fixed_score', 'start_time', 'profit_percentage')
    list_filter = ('start_time', 'profit_percentage')
    search_fields = ('home_team', 'away_team', 'fixed_score')
    ordering = ('-start_time',)
    readonly_fields = ('fixed_score',)  # Optional, if you want fixed score to be uneditable
    fieldsets = (
        (None, {
            'fields': ('home_team', 'away_team', 'fixed_score', 'start_time', 'profit_percentage')
        }),
    )

class ShowcaseSliderAdmin(admin.ModelAdmin):
    # Show image preview in the admin list view
    list_display = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

    # Ensure the image is deleted when the entry is deleted from admin
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

class soccer_sliderAdmin(admin.ModelAdmin):
    # Show image preview in the admin list view
    list_display = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

    # Ensure the image is deleted when the entry is deleted from admin
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()    

class leagues_sliderAdmin(admin.ModelAdmin):
    # Show image preview in the admin list view
    list_display = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

    # Ensure the image is deleted when the entry is deleted from admin
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()                        


class PremierLeagueGameAdmin(admin.ModelAdmin):
    list_display = ('match','start_time', 'fixed_score', 'profit_percentage')
    search_fields = ('match',)

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'daily_interest', 'withdrawal_frequency')  # Customize fields displayed
    search_fields = ('name',)  # Add search functionality by name
    list_filter = ('withdrawal_frequency',)  # Filter by withdrawal frequency

@admin.register(FootballMatch)
class FootballMatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'start_time', 'fixed_score', 'profit_percentage', 'match_type')
    list_filter = ('match_type', 'start_time')
    search_fields = ('home_team', 'away_team')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_name', 'start_time', 'fixed_score', 'profit_percentage', 'league')  # Use start_time instead of match_date/match_time
    list_filter = ('league',)
    search_fields = ('match_name',)

class BetHistoryAdmin(admin.ModelAdmin):
    list_display = ('match', 'date', 'time', 'fixed_score', 'profit_percentage', 'bet_amount', 'user','placed_at')
    list_filter = ('date', 'user')  # Allows filtering by date and user
    search_fields = ('match',)  # Enables search functionality for the match field
    ordering = ('-date',)  # Orders by date descending

  
    fieldsets = (
        (None, {
            'fields': ('user', 'match', 'date', 'time', 'fixed_score', 'profit_percentage', 'bet_amount')
        }),
    )
    readonly_fields = ('date',)  # Make the date field read-only

admin.site.register(BetHistory, BetHistoryAdmin)




class DepositRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'method', 'date', 'status', 'confirm_button', 'decline_button')
    list_filter = ('status', 'method', 'user')
    search_fields = ('user__username', 'amount')

    def confirm_button(self, obj):
        if obj.status == 'Pending':
            return format_html(
                '<a class="btn btn-primary" href="{}">Confirm</a>',
                reverse('confirm_deposit') + f'?deposit_id={obj.pk}'
            )
        return ''

    def decline_button(self, obj):
        if obj.status == 'Pending':
            return format_html(
                '<a class="btn btn-danger" href="{}">Decline</a>',
                reverse('decline_deposit') + f'?deposit_id={obj.pk}'
            )
        return ''

    confirm_button.short_description = 'Confirm'
    decline_button.short_description = 'Decline'

class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'method', 'date', 'status', 'confirm_button', 'decline_button')
    list_filter = ('status', 'method', 'user')
    search_fields = ('user__username', 'amount')

    def confirm_button(self, obj):
        if obj.status == 'Pending':
            return format_html(
                '<a class="btn btn-primary" href="{}">Confirm</a>',
                reverse('confirm_withdrawal') + f'?withdraw_id={obj.pk}'
            )
        return ''

    def decline_button(self, obj):
        if obj.status == 'Pending':
            return format_html(
                '<a class="btn btn-danger" href="{}">Decline</a>',
                reverse('decline_withdrawal') + f'?withdraw_id={obj.pk}'
            )
        return ''

    confirm_button.short_description = 'Confirm'
    decline_button.short_description = 'Decline'





admin.site.register(ReferralBonus)
admin.site.register(PurchasePackage)
admin.site.register(AdminBankAccount)
admin.site.register(DepositRequest, DepositRequestAdmin)
admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)
admin.site.register(PremierLeagueGame, PremierLeagueGameAdmin)
# Register the model with the custom admin configuration
soccer_slider
admin.site.register(ShowcaseSlider, ShowcaseSliderAdmin)
admin.site.register(soccer_slider, soccer_sliderAdmin)
# Register the models
admin.site.register(leagues_slider, leagues_sliderAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(UsersReferralPercentage, UsersReferralPercentageAdmin)
admin.site.register(UsersBankDetail, UsersBankDetailsAdmin)
admin.site.register(UserBalance, UserBalanceAdmin)


