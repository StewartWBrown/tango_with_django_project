from django.shortcuts import render
from django.http import HttpResponse

# Import the Category model and page model(chapter 6)

from rango.models import Category
from rango.models import Page

## Import the form stuff (chapter 7)
from rango.forms import CategoryForm
from rango.forms import PageForm

## import user stuff

from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def index(request):
        # Query the database for a list of the catagories stored
        # ordered by number of likes, decending order
        # take top 5 and place the list in context_dict dictionary
        # pass context_dict to the template engine

        pages_list = Page.objects.order_by('-views')[:5]
        category_list = Category.objects.order_by('-likes')[:5]
        context_dict = {'categories': category_list, 'pages': pages_list}

        #render the response and send it back

        return render(request, 'rango/index.html', context_dict)

def about(request):
        context_dict = {}
        return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
        # Create context dict to pass to template rendering engine

        context_dict = {}

        try:
                category = Category.objects.get(slug=category_name_slug)
                pages = Page.objects.filter(category=category)

                context_dict['pages'] = pages
                context_dict['category'] = category
                
        except Category.DoesNotExist:
                #get here if didnt find specified category

                context_dict['category']= None
                context_dict['pages'] = None

        return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
	
	form = CategoryForm()

	#A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)
	
	# Have we been provided with a valid form?
	if form.is_valid():
		# Save the new category to the database.
		form.save(commit=True)
		return index(request)
	
	else:
		print(form.errors)
		return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
        try:
                category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
                category = None

        form = PageForm()
        if request.method == 'POST':
                form = PageForm(request.POST)
                if form.is_valid():
                        if category:
                                page = form.save(commit=False)
                                page.category = category
                                page.views = 0
                                page.save()
                                return show_category(request, category_name_slug)
                else:
                        print(form.errors)

        context_dict = {'form':form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)

        

def register(request):
        #Code changes value to
        # True when registration succeeds.
        registered = False

        # If it's a HTTP POST, we're interested in processing form data.
        if request.method == 'POST':
                # Attempt to grab information from the raw form information.
                user_form = UserForm(data=request.POST)
                profile_form = UserProfileForm(data=request.POST)

                if user_form.is_valid() and profile_form.is_valid():
                        # Save the user's form data to the database.
                        user = user_form.save()

                        user.set_password(user.password)
                        user.save()

                        # Now sort out the UserProfile instance.
                        profile = profile_form.save(commit=False)
                        profile.user = user

                        # Did the user provide a profile picture?                
                        if 'picture' in request.FILES:
                                profile.picture = request.FILES['picture']

                        profile.save()

                        # Update our variable. registration was successful.
                        registered = True
                else:
                        print(user_form.errors, profile_form.errors)
        else:
                # Not a HTTP POST, so we render our form using two ModelForm instances.
                # These forms will be blank, ready for user input.
                user_form = UserForm()
                profile_form = UserProfileForm()

        # Render the template depending on the context.
        return render(request,
                'rango/register.html',
                {'user_form': user_form,
                'profile_form': profile_form,
                'registered': registered})

def user_login(request):
        # If the request is a HTTP POST, try to pull out the relevant information.
        if request.method == 'POST':
                # Gather the username and password provided by the user.
                username = request.POST.get('username')
                password = request.POST.get('password')

                # Check username valid
                user = authenticate(username=username, password=password)

                if user:
                        # Is the account active? It could have been disabled.
                        if user.is_active:
                                login(request, user)
                                return HttpResponseRedirect(reverse('index'))
                        else:
                                return HttpResponse("Your Rango account is disabled.")
                else:
                        print("Invalid login details: {0}, {1}".format(username, password))
                        print("Wrong username or password, :( try again!")
                        return HttpResponse("Invalid login details supplied.")
        else:
                return render(request, 'rango/login.html', {})


def some_view(request):
        if not request.user.is_authenticated():
                return HttpResponse("You are logged in.")
        else:
                return HttpResponse("You are not logged in.")

@login_required
def restricted(request):
        return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
        # Since we know the user is logged in, we can now just log them out.
        logout(request)
        # Take the user back to the homepage.
        return HttpResponseRedirect(reverse('index'))


