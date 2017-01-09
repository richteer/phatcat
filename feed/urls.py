from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets, mixins
from .models import Cat, Feeder, Fed
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import list_route
from rest_framework.routers import Route, DynamicListRoute, SimpleRouter

# TODO: REDO EVERYTHING WITH A IsOwnerOrReadOnly-like PERMISSION


class CatSerializer(serializers.ModelSerializer):
	class Meta:
		model = Cat
		fields = '__all__'

# TODO: Use Permissions here?
class CatViewSet(mixins.DestroyModelMixin,
				 mixins.CreateModelMixin,
				 viewsets.GenericViewSet):
	queryset = Cat.objects.all()
	serializer_class = CatSerializer

	# Force cat owner to be the POSTer
	# Create a Feeder instance for owner as well
	def perform_create(self, serializer):
		cat = serializer.save(owner=self.request.user)
		Feeder.objects.create(user=self.request.user, cat=cat)

	def list(self, request):
		queryset = Cat.objects.filter(owner=request.user.id)
		serializer = CatSerializer(queryset, many=True)
		return Response(serializer.data)

	def retrieve(self, request, pk=None):
		if not pk:
			return Response() # TODO: return errors here
		q = Feeder.objects.filter(user=request.user, cat=pk)
		if not q:
			return Response()
		serializer = CatSerializer(q[0].cat)
		return Response(serializer.data)

	def perform_destroy(self, instance):
		if self.request.user != instance.owner:
			return ValidationError("Cannot delete a cat you don't own")
		return


	@list_route()
	def data(self, request, pk=None):
		cat = Cat.objects.get(pk=pk)
		data = Fed.objects.filter(cat=cat)
		return Response(FedSerializer(data, many=True).data)

# TODO: Also send back the owned, and feeding cats
class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'email')

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all() # TODO: Limit to only the auth'd user's info
	serializer_class = UserSerializer

class FeederSerializer(serializers.ModelSerializer):
	class Meta:
		model = Feeder
		fields = '__all__'

class FeederViewSet(mixins.DestroyModelMixin,
					viewsets.GenericViewSet):
	queryset = Feeder.objects.all() # TODO: NOT do this
	serializer_class = FeederSerializer

	def list(self, request):
		queryset = Feeder.objects.filter(user=request.user)
		serializer = FeederSerializer(queryset, many=True)
		return Response(serializer.data)

	def create(self, request):
		q = Cat.objects.get(pk=int(request.data.get("cat",0)))
		if not q:
			return
		if q.owner != request.user:
			return Response("Cannot assign a feeder for a cat you don't own")

		if Feeder.objects.filter(cat=q, user=User.objects.get(int(request.data.get("user")))).exists():
			return Response("Feeder assignment already exists")

		f = Feeder.objects.create(cat=q, user=User.objects.get(int(request.data.get("user"))))
		return Response(FeederSerializer(f).data)

	def retrieve(self, request, pk=None):
		if not pk:
			return Response("No pk?")
		q = Feeder.objects.get(pk=pk)
		if not q:
			return Response("404")
		if request.user == q.user or request.user == q.cat.owner:
			return Response(FeederSerializer(q).data)
		return Response("eh?")

	def perform_destroy(self, instance):
		if instance.user != self.request.user and instance.cat.owner != self.request.user:
			return ValidationError("You are not the cat owner nor the Feeder in question")
		if instance.user == self.request.user and instance.cat.owner == self.request.user:
			return ValidationError("You can't delete the feeder if you are the owner")

		instance.delete()


class FedSerializer(serializers.ModelSerializer):
	class Meta:
		model = Fed
		fields = '__all__'
		depth = 1

class FedViewSet(mixins.CreateModelMixin,
				 mixins.DestroyModelMixin,
				 viewsets.GenericViewSet):

	queryset = Fed.objects.none()
	serializer_class = FedSerializer

	# TODO: Make sure the user feeds the cat -> validator?
	def perform_create(self, serializer):
		serializer.save(by=self.request.user)

	def perform_destroy(self, instance):
		# Must be a feeder for the cat
		if instance.cat not in Feeder.objects.filter(user=self.request.user):
			return
		instance.delete()
		


# Routers provide an easy way of automatically determining the URL conf.
'''catrouter = routers.DefaultRouter()
catrouter.register(r'cat', CatViewSet)
userrouter = routers.DefaultRouter()
userrouter.register(r'user', UserViewSet)
'''
router = routers.DefaultRouter()
#router.register(r'cat', CatViewSet)
router.register(r'user', UserViewSet)
router.register(r'feeder', FeederViewSet)
router.register(r'fed', FedViewSet)

class CustomCatRouter(SimpleRouter):
	routes = [
		Route(
			url=r"^{prefix}/$",
			mapping={"get":"list", "post":"create"},
			name="{basename}-list",
			initkwargs={"suffix":"List"}
		),
		Route(
			url=r"^{prefix}/{lookup}/$",
			mapping={"get":"retrieve", "delete":"destroy"},
			name="{basename}-detail",
			initkwargs={"suffix":"Detail"}
		),
		DynamicListRoute(
			url=r"^{prefix}/{lookup}/{methodnamehyphen}/$",
#			mapping={"get":"list", "post":"create"},
			name="{basename}-{methodnamehyphen}",
			initkwargs={"suffix":"Data"}
		)
	]			

catrouter = CustomCatRouter()
catrouter.register(r'cat', CatViewSet, base_name='cat')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
#	url(r'^cat/', include(catrouter.urls)),
#	url(r'^user/', include(userrouter.urls)),
	url(r'^', include(router.urls))
]
urlpatterns += catrouter.urls
