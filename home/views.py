from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def test_message(request):
    # Using request.build_absolute_uri to generate a full URL that the Flutter app can access
    image_url = request.build_absolute_uri('/static/images/logo.JPG')
    return Response({
        "message": "Hello Mai English Center",
        "image_url": image_url
    })

def index(request):
    return render(request, 'index.html')
