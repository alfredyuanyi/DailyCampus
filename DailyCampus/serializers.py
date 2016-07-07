from DailyCampus.models import *
from rest_framework_mongoengine.serializers import DocumentSerializer
class UserSerializer(DocumentSerializer):
	class Meta:
		model = User 

class ConcernsSerializer(DocumentSerializer):
	class Meta:
		model = Concerns 
		
