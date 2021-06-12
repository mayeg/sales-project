from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class UserView(APIView):
    def post(self, request):
        data = request.data
        user_exist = User.objects.filter(username=data['username']).first()
        if user_exist:
            response_status = status.HTTP_400_BAD_REQUEST
            response = {"message": 'Ya existe un usuario con ese nombre'}
            return Response(response, response_status)

        user_create = User.objects.create_user(
            username=data['username'],
            password=data['password']
        )
        if user_create:
            response_status = status.HTTP_200_OK
            response = {"message": 'Usuario creado'}
        else:
            response_status = status.HTTP_400_BAD_REQUEST
            response = {"message": 'Ha ocurrido un errror inesperado'}

        return Response(response, response_status)

