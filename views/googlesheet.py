from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions

from integration.serializers.googlesheet import GoogleSheetIntegrationSerializer
from integration.models.googlesheet import GoogleSheetIntegration


class GoogleSheetIntegrationViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows users to be created, viewed, edited or deleted.
	"""	
	serializer_class = GoogleSheetIntegrationSerializer

	def get_queryset(self):

		queryset = GoogleSheetIntegration.objects.all().order_by('-id')

		return queryset
	
	def get_permissions(self):

		permission_classes = [permissions.IsAuthenticated, ]

		return super(GoogleSheetIntegrationViewSet, self).get_permissions()

	def get_serializer_context(self):
		context = super(GoogleSheetIntegrationViewSet, self).get_serializer_context()
		context['poll_id'] = self.kwargs.get('poll_id')
		context['survey_id'] = self.kwargs.get('survey_id')
		context['user'] = self.request.user
		context['request'] = self.request
		return context
