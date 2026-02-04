from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def logs(request):
    return render(request, 'utilitarios/logs.html')
