from django.http import HttpResponse

def index(request):
        return HttpResponse("Rango says hey there partner!")

def about(request):
        return HttpResponse("Rango says here is the about page. <br> <a href='/rango/'>index</a>")
