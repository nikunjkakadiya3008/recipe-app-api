from django.shortcuts import render
from rest_framework.settings import api_settings
from rest_framework import generics , authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import permissions
from . import serializers

class UserView(generics.CreateAPIView):
    serializer_class =serializers.UserSerializer

class TokenView(ObtainAuthToken):
    serializer_class = serializers.TokenSerializer
    renderer_classes =api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class  = serializers.UserSerializer
    authentication_classes = [authentication.TokenAuthentication,]
    permission_classes =[permissions.IsAuthenticated,]
    
    def get_object(self):
        return self.request.user