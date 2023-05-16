from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel, CarMake, CarDealer
from .restapis import post_request, get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
# Create an `about` view to render a static about page
def about(request):
    if request.method=="GET":
        return render(request, 'djangoapp/about.html')
    
# Create a `contact` view to return a static contact page
def contact(request):
    if request.method=="GET":
        return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
    return redirect('djangoapp:index')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/cd3b050b-d3fd-4e7e-87b1-c696eff9ebb6/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        # Return a list of dealer short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        return HttpResponse(dealer_names)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        dealer_url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/cd3b050b-d3fd-4e7e-87b1-c696eff9ebb6/dealership-package/get-dealership"
        review_url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/cd3b050b-d3fd-4e7e-87b1-c696eff9ebb6/dealership-package/get-review"
        # Get reviews from the URL
        reviews = get_dealer_reviews_from_cf(review_url, dealer_id)
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
        context['reviews'] = reviews
        context['dealer'] = dealer
        # Return a list of reviewer names
        reviewer_names = ' '.join([review.sentiment for review in reviews])
        return HttpResponse(reviewer_names)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    dealer_url      = "https://eu-gb.functions.appdomain.cloud/api/v1/web/cd3b050b-d3fd-4e7e-87b1-c696eff9ebb6/dealership-package/get-dealership"
    postreview_url  = "https://eu-gb.functions.cloud.ibm.com/api/v1/namespaces/cd3b050b-d3fd-4e7e-87b1-c696eff9ebb6/actions/dealership-package/post-review"
    
    context = {}
    dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
    context['dealer'] = dealer
    if request.method == 'GET':
        cars = CarModel.objects.all()
        context['cars'] = cars
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            payload = dict()
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = dealer_id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            payload["purchase_date"] = request.POST["purchasedate"]
            payload["car_make"] = car.car_make.name
            payload["car_model"] = car.name
            payload["car_year"] = int(car.year.strftime("%Y"))
            json_payload = {}
            json_payload["review"] = payload
            post_request(postreview_url, json_payload, dealerId=dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
 