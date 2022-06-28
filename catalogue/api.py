from catalogue.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.db.models import Case, CharField, Value, When
from django.contrib.auth.models import User
from catalogue.models import *
import json

class AllLoggers(APIView):

    def get(self, request, format=None):

        data = {

        }
        print(data)


        return Response(data)