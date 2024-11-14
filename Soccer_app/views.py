from django.shortcuts import render
from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse
from accounts.models import HotGame,ShowcaseSlider,PremierLeagueGame,Package,FootballMatch,Match,BetHistory,DepositRequest,WithdrawalRequest,soccer_slider,leagues_slider
import requests 
from django.core.paginator import Paginator
from django.conf.urls.static import static

# Create your views here.
def home(request):
    hot_games = HotGame.objects.all()
    slides = ShowcaseSlider.objects.all()
    games = PremierLeagueGame.objects.all()
    return render(request,'home/index.html',
        {
        'hot_games': hot_games,
        'slides': slides,
        'games': games
        })

def profile(request):
    return render(request,'home/profile.html')

def bank_account(request):
    return render(request,'home/bank_account.html')

def parkages(request):
    packages = Package.objects.all()
    return render(request,'home/parkages.html', {'packages': packages})

def Deposit(request):
    Deposit_history = DepositRequest.objects.filter(user=request.user) 
    context = {
        'Deposit_history': Deposit_history,
    }
    return render(request,'home/Deposit.html',context)

def Withdraw(request):
    withdrawal_history = WithdrawalRequest.objects.filter(user=request.user) 
    context = {
        'withdrawal_history':withdrawal_history,
    }
    return render(request,'home/Withdraw.html',context)

def football(request):
    football_matches = FootballMatch.objects.all()
    slides = soccer_slider.objects.all()
    context = {
        'slides': slides,
        'football_matches': football_matches,
    }
    return render(request,'home/football.html',context)

leagues_slider

def league(request):
    premier_league_matches = Match.objects.filter(league='PL')
    la_liga_matches = Match.objects.filter(league='LL')
    bundesliga_matches = Match.objects.filter(league='BL')
    serie_a_matches = Match.objects.filter(league='SA')
    slides = leagues_slider.objects.all()
    context = {
        'premier_league_matches': premier_league_matches,
        'la_liga_matches': la_liga_matches,
        'bundesliga_matches': bundesliga_matches,
        'serie_a_matches': serie_a_matches,
        'slides': slides,
    }
    return render(request,'home/league.html',context)





def beting_history(request):
    # Determine the current tab (default to 'bets' if no tab is specified)
    tab = request.GET.get('tab', 'bets')  # Default to 'bets'

    # Fetching all bets for the logged-in user, ordered by the placement date
    bets = BetHistory.objects.filter(user=request.user).order_by('-placed_at')
    
    # Filter bets based on status
    playing_bets = bets.filter(status='playing').order_by('-placed_at')
    won_bets = bets.filter(status='won').order_by('-placed_at')
    lost_bets = bets.filter(status='lost').order_by('-placed_at')

    # Pagination for each status
    playing_paginator = Paginator(playing_bets, 3)
    won_paginator = Paginator(won_bets, 3)
    lost_paginator = Paginator(lost_bets, 3)

    # Get the page number from the query parameters (default to 1)
    page_number = request.GET.get('page', 1)

    # Based on the selected tab, get the appropriate page
    if tab == 'wins':
        page = won_paginator.get_page(page_number)
    elif tab == 'losses':
        page = lost_paginator.get_page(page_number)
    else:  # Default to 'bets'
        page = playing_paginator.get_page(page_number)

    context = {
        'playing_bets': playing_paginator.get_page(page_number),
        'won_bets': won_paginator.get_page(page_number),
        'lost_bets': lost_paginator.get_page(page_number),
        'current_tab': tab,  # Pass the current tab to the template
        'page': page,        # Pass the current page object for pagination
    }

    return render(request, 'home/beting_history.html', context)





def custom_404_view(request, exception):
    return render(request, 'home/404.html', status=404)

def custom_500_view(request):
    return render(request, 'home/500.html', status=500)