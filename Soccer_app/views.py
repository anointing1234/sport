from django.shortcuts import render
from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse
from accounts.models import HotGame,ShowcaseSlider,PremierLeagueGame,Package,FootballMatch,Match,BetHistory,DepositRequest,WithdrawalRequest
import requests 
from django.core.paginator import Paginator

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
    context = {
        'football_matches': football_matches,
    }
    return render(request,'home/football.html',context)



def league(request):
    premier_league_matches = Match.objects.filter(league='PL')
    la_liga_matches = Match.objects.filter(league='LL')
    bundesliga_matches = Match.objects.filter(league='BL')
    serie_a_matches = Match.objects.filter(league='SA')
    context = {
        'premier_league_matches': premier_league_matches,
        'la_liga_matches': la_liga_matches,
        'bundesliga_matches': bundesliga_matches,
        'serie_a_matches': serie_a_matches,
    }
    return render(request,'home/league.html',context)







def beting_history(request):
    # Determine the current tab
    tab = request.GET.get('tab', 'bets')  # Default to 'bets' if no tab is specified

    # Fetching bets, wins, and losses with ordering applied
    bets = BetHistory.objects.filter(user=request.user).order_by('-date')
    wins = bets.filter(profit_percentage__gt=0).order_by('-date')
    losses = bets.filter(profit_percentage__lte=0).order_by('-date')

    # Pagination
    bets_paginator = Paginator(bets, 3)
    wins_paginator = Paginator(wins, 3)
    losses_paginator = Paginator(losses, 3)

    # Get the page number from query parameters
    page_number = request.GET.get('page', 1)
    if tab == 'wins':
        page = wins_paginator.get_page(page_number)
    elif tab == 'losses':
        page = losses_paginator.get_page(page_number)
    else:
        page = bets_paginator.get_page(page_number)

    context = {
        'bets': bets_paginator.get_page(page_number),
        'wins': wins_paginator.get_page(page_number),
        'losses': losses_paginator.get_page(page_number),
        'current_tab': tab,  # Pass the current tab to the context
        'page': page,        # Pass the current page data
    }

    return render(request, 'home/beting_history.html', context)


def custom_404_view(request, exception):
    return render(request, 'home/404.html', status=404)

def custom_500_view(request):
    return render(request, 'home/500.html', status=500)