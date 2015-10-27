from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
from django.core.urlresolvers import reverse

# Create your views here.

# def index(request):
#
#     category_list = Category.objects.all()
#     page_list = Page.objects.order_by('-views')[:5]
#     context_dict = {'categories': category_list, 'pages': page_list}
#
#     # Get the number of visits to the site.
#     # We use the COOKIES.get() function to obtain the visits cookie.
#     # If the cookie exists, the value returned is casted to an integer.
#     # If the cookie doesn't exist, we default to zero and cast that.
#     visits = int(request.COOKIES.get('visits', '1'))
#
#     reset_last_visit_time = False
#     response = render(request, 'rango/index.html', context_dict)
#     # Does the cookie last_visit exist?
#     if 'last_visit' in request.COOKIES:
#         # Yes it does! Get the cookie's value.
#         last_visit = request.COOKIES['last_visit']
#         # Cast the value to a Python date/time object.
#         last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
#
#         # If it's been more than a day since the last visit...
#         if (datetime.now() - last_visit_time).seconds > 2:
#             visits = visits + 1
#             # ...and flag that the cookie last visit needs to be updated
#             reset_last_visit_time = True
#     else:
#         # Cookie last_visit doesn't exist, so flag that it should be set.
#         reset_last_visit_time = True
#
#         context_dict['visits'] = visits
#
#         #Obtain our Response object early so we can add cookie information.
#         response = render(request, 'rango/index.html', context_dict)
#
#     if reset_last_visit_time:
#         response.set_cookie('last_visit', datetime.now())
#         response.set_cookie('visits', visits)
#
#     # Return response back to the user, updating any cookies that need changed.
#     return response

def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response


def about(request):
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    return render(request, 'rango/about.html', {'visits': count})

def schedule(request):
    return HttpResponse("Schedule")

def category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_slug']=category_name_slug
    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    # A HTTP PO
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)

            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                return category(request, category_name_slug)
        else:
            print form.errors

    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat}

    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    registered = False

    # if request.session.test_cookie_worked():
    #     print ">>>> TEST COOKIE WORKED!"
    #     request.session.delete_test_cookie()

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)


        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

                profile.save()

                registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                    'rango/register.html',
                    {'user_form': user_form, 'profile_form': profile_form,
                    'registered': registered})


def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango')
            else:
                return HttpResponse('Your Rango account is disabled')
        else:
            print "Invalid login details:{0}, {1}".format(username, password)
            context = {}
            context['erorrs'] = 'error'
            return redirect('/rango', context)
            # return HttpResponse("Invalid login details supplied")

    else:
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return redirect('rango/restricted.html')



# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')