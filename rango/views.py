from django.shortcuts import render
from django.http import HttpResponse

# Import the Category model and page model(chapter 6)

from rango.models import Category
from rango.models import Page

## Import the form stuff (chapter 7)
from rango.forms import CategoryForm
from rango.forms import PageForm


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

        
