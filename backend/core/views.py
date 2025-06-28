from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Entry
from .forms import EntryForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import timedelta
import os
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt  
from django.conf import settings



def calculate_streaks(entries):
    if not entries:
        return 0, 0

    dates = sorted({entry.created_at.date() for entry in entries}, reverse=True)

    current_streak = 0
    longest_streak = 0
    today = timezone.localdate()
    previous_date = today

    for date in dates:
        if previous_date - date <= timedelta(days=1):
            current_streak += 1
            previous_date = date
        else:
            break

    streak = 1
    for i in range(1, len(dates)):
        if (dates[i-1] - dates[i]) == timedelta(days=1):
            streak += 1
        else:
            longest_streak = max(longest_streak, streak)
            streak = 1
    longest_streak = max(longest_streak, streak)

    return current_streak, longest_streak


def home(request):
    return render(request, 'journal/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password1)
        messages.success(request, "Registration successful. Please log in.")
        return redirect('login')

    return render(request, 'journal/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')

    return render(request, 'journal/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    entries = Entry.objects.filter(user=request.user).order_by('-created_at')

    for entry in entries:
        entry.check_decay()

    total_entries = entries.count()
    growing_entries = entries.filter(is_dead=False).count()
    dead_entries = entries.filter(is_dead=True).count()
    current_streak, longest_streak = calculate_streaks(entries)

    return render(request, 'journal/dashboard.html', {
        'entries': entries,
        'total_entries': total_entries,
        'growing_entries': growing_entries,
        'dead_entries': dead_entries,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
    })


@login_required
def renew_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)

    # ✅ DO NOT CALL is_dead like a function
    if entry.is_dead:
        entry.is_dead = False
        entry.last_watered = timezone.now()
        entry.save()

    return redirect('view_entry', entry_id=entry.id)


@login_required
def create_entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('dashboard')
    else:
        form = EntryForm()
    return render(request, 'journal/create.html', {'form': form})

@login_required
def water_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)
    if not entry.is_dead:
        entry.last_watered = timezone.now()
        entry.save()
    return redirect('dashboard')

@login_required
def view_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)
    return render(request, 'journal/view_entry.html', {'entry': entry})

@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)

    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EntryForm(instance=entry)

    return render(request, 'journal/edit_entry.html', {'form': form, 'entry': entry})

@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)

    if request.method == 'POST':
        entry.delete()
        return redirect('dashboard')

    return render(request, 'journal/delete_entry.html', {'entry': entry})



def god_message(request):
    message = None
    selected_mood = None

    if request.method == 'POST':
        selected_mood = request.POST.get('mood')
        prompt = f"Give a short, comforting, spiritual message for someone who is feeling {selected_mood}."

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30)
            res.raise_for_status()
            message = res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print("Error:", e)
            message = "⚠️ God's message line seems busy. Try again later."

    return render(request, 'journal/god_message.html', {
        'message': message,
        'selected_mood': selected_mood
    })