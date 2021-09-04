from django.http.response import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django import forms

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label = "Entry title", widget=forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 10}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entrypage(request, title):
    if util.get_entry(title) is None:
        raise Http404
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": util.get_entry(title),
            "title": title
        })

def search(request):
    query = request.GET.get('q','')
    if (util.get_entry(query) is not None):
        return HttpResponseRedirect(reverse("entrypage", kwargs={'title' : query }))
    else:
        subStringEntries = []
        for entry in util.list_entries():
            if query.upper() in entry.upper():
                subStringEntries.append(entry)
        
        if len(subStringEntries) == 0:
            return render(request, "encyclopedia/entrylist.html")
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": subStringEntries,
                "search": True,
                "value": query
            })

def newpage(request):
    if request.method == 'POST':
        if util.get_entry(request.GET.get('title')) is not None:
            return render(request, "encyclopedia/pageexists.html")
        else:
            title = request.POST.get('title')
            content = request.POST.get('content')
            util.save_entry(title,content)
            return render(request, "encyclopedia/entry.html")
    else:
        return render(request, "encyclopedia/newpage.html")

def newentry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry' : title}))
            else:
                return render(request, "encyclopedia/pageexists.html", {  #recheck html
                "form": form,
                "existing": True,
                "entry" : title
                })
        else:
            return render(request, "encyclopedia/pageexists.html", {
                "form" : form,
                "existing" : False
            })
    else:
        return render(request,"encyclopedia/pageexists.html", {
            "form" : NewEntryForm(),
            "existing" : False
        })
