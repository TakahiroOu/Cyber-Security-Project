from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Question, Choice

#fix5: add this:
#from .models import Vote

from django.http import Http404
from django.db.models import F
from django.urls import reverse
from django.db import connection
from django.contrib.auth.models import User
from django.core.cache import cache

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)

#Vulnerability2
def detail(request, question_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id, question_text, pub_date "
            f"FROM polls_question WHERE id = {question_id}"
        )
        row = cursor.fetchone()

    if row is None:
        raise Http404("Question does not exist")

    question = Question(
        id=row[0],
        question_text=row[1],
        pub_date=row[2]
    )

    return render(request, "polls/detail.html", {"question": question})
# FIX2:
# Replace the vulnerable code above with this code:
#
# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/detail.html", {"question": question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

# FIX1:
#Add this right before def vote():
#
# @login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    #Fix 5:
    #Add the code to def vote():
    #
    #if Vote.objects.filter(user=request.user, question=question).exists():
    #    return render(
    #        request,
    #        "polls/detail.html",
    #        {
    #            "question": question,
    #            "error_message": "You have already voted.",
    #        },
    #    )
    
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()

        #Fix5:
        #Add this code to def vote():
        #
        # Vote.objects.create(
        #   user=request.user,
        #    question=question)

        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("polls:index"))

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # VULNERABLE: unlimited login attempts
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("polls:index"))

        return render(
            request,
            "polls/login.html",
            {
                "error_message": "Invalid username or password."
            },
        )

    return render(request, "polls/login.html")


# FIX3:
# Replace the vulnerable login_view above with the following:
#
# def login_view(request):
#     if request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("polls:index"))
#
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#
#         attempt_key = f"login_attempts_{request.META.get('REMOTE_ADDR')}"
#         attempts = cache.get(attempt_key, 0)
#
#         if attempts >= 5:
#             return render(
#                 request,
#                 "polls/login.html",
#                 {
#                     "error_message":
#                     "Too many login attempts. Please try again later."
#                 },
#             )
#
#         user = authenticate(
#             request,
#             username=username,
#             password=password
#         )
#
#         if user is not None:
#             cache.delete(attempt_key)
#             login(request, user)
#             return HttpResponseRedirect(reverse("polls:index"))
#
#         cache.set(attempt_key, attempts + 1, 300)
#
#         return render(
#             request,
#             "polls/login.html",
#             {
#                 "error_message": "Invalid username or password."
#             },
#         )
#
#     return render(request, "polls/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("polls:index"))