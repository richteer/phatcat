from rest_framework import permissions
from feed.models import Feeder

# Can only operate on a cat a user "owns"
class IsCatOwner(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):
		return obj.owner == request.user

class IsFeeder(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return not not Feeder.objects.filter(user=request.user, cat=obj)
		return False
