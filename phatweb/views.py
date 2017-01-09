from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from feed.models import Cat, Feeder, Fed
from feed.urls import FedSerializer

# Create your views here.
@login_required
def root(request):
	return HttpResponse("not implemented")

@login_required
def cat(request):
	return HttpResponse("test")


@login_required
def cat_detail(request, id):
	cat = Cat.objects.get(pk=id)
	if not cat:
		return HttpResponse("not impl")

	return render(request, 'cat_detail.html', {"cat":cat})

