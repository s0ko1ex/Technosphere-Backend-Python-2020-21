from django.shortcuts import render
from .models import Lock

# Create your views here.
def lock_index(request):
    locks = Lock.objects.all()
    context = {
        'locks' : locks
    }
    return render(request, "lock_index.html", context)

def lock_detail(request, id):
    lock = Lock.objects.get(id=id)
    context = {
        'lock' : lock
    }
    return render(request, "lock_detail.html", context)

