from rest_framework import views
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


class LimitedAPIView(views.APIView):

    renderer_classes = [JSONRenderer]

    def get(self, request):
        return Response({"Limited Api": "Don't overuse me."})

class UnlimitedAPIView(views.APIView):

    renderer_classes = [JSONRenderer]

    def get(self, request):
        return Response({"Unlimited Api": "Use me as much as you want."})
