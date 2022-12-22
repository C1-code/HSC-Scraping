from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render

import Data

graph_div = ""

def index(request):
    schools = Data.getList(2022, item="School")
    subjects = Data.getList(2022, item="Subject")
    template = loader.get_template('index.html')

    context = {
        'schools': schools,
        'subjects': subjects,
        'graph_div': graph_div
    }
    return HttpResponse(template.render(context, request))

def updateGraph(request):
    global graph_div
    school = request.POST["schools"]
    subject = request.POST["subjects"]
    graph_div = Data.graph(school, subject)
    return HttpResponseRedirect(reverse('index'))
