from django.shortcuts import render
from .models import Lock
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import JSONParser
from .serializers import LockSerializer

from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.shortcuts import reverse

def login(request):
    return render(request, 'login.html')


def lock_index(request):
    locks = Lock.objects.all()
    context = {
        'locks' : locks,
        'authenticated': request.user.is_authenticated
    }
    return render(request, "lock_index.html", context)


@login_required
def lock_detail(request, id):
    lock = Lock.objects.get(id=id)
    context = {
        'lock' : lock
    }
    return render(request, "lock_detail.html", context)

def authentified_decorator(func):
    def decorator(*args, **kwargs):
        if isinstance(args[-1], Request) or\
                isinstance(kwargs.get('request', None), Request):
            user = args[-1].user
            if user.is_authenticated:
                return func(*args, **kwargs)
            else:
                return Response({'User is not authenticated!'}, status.HTTP_401_UNAUTHORIZED)
        else:
            raise ValueError("No request provided!")
    
    return decorator


class LockView(APIView):
    def get(self, request):
        id = request.query_params.get('id', None)
        if id:
            try:
                lock = Lock.objects.get(id=id)
            except Lock.DoesNotExist as e:
                return Response({str(e)}, status.HTTP_404_NOT_FOUND)
            serializer = LockSerializer(lock)
            return Response({'data': serializer.data}, status.HTTP_200_OK)
        else:
            locks = Lock.objects.all()
            serializer = LockSerializer(locks, many=True)
            return Response({'data': serializer.data, 'n': len(locks)}, status.HTTP_200_OK)
    
    @authentified_decorator
    def post(self, request):
        data = dict(request.data)
        if "name" not in data:
            return Response({"No mandatory name provided!"}, status.HTTP_404_NOT_FOUND)

        serializer = LockSerializer(data=data, many=isinstance(data, list))

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_404_NOT_FOUND)
        return Response({})
    
    @authentified_decorator
    def put(self, request):
        data = dict(request.data)
        if 'id' not in data:
            return Response({"No id!"}, status.HTTP_404_NOT_FOUND)
        
        lock = Lock.objects.get(id=data['id'])
        serializer = LockSerializer(lock, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_404_NOT_FOUND)
    
    @authentified_decorator
    def delete(self, request):
        id = request.query_params.get('id', None)
        if id:
            try:
                lock = Lock.objects.get(id=id)
            except Lock.DoesNotExist as e:
                return Response({str(e)}, status.HTTP_404_NOT_FOUND)
            lock.delete()
            return Response({f"Lock with id={id} deleted"}, status.HTTP_404_NOT_FOUND)
        else:
            return Response({"No id provided!"}, status.HTTP_404_NOT_FOUND)
        return Response({})