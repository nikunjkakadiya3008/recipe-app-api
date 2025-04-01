from django.shortcuts import render
from rest_framework import viewsets ,mixins , status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from . import serializers
from core import models

from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)




@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ]
    )
)
class RecipeViewsets(viewsets.ModelViewSet):
    serializer_class = serializers.RecipeDetailSerializer
    queryset = models.Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes=(IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        if tags :
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user = self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.RecipeSerializer
        # it will check the method that if the method is list(simple get then it will use RecipeSerializer otherwise it will use RecipeDetailSerializer)
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        if pk is not None:
            recipe = models.Recipe.objects.get(pk = pk)
        # recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            ),
        ]
    )
)
class TagViewSet(mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin ,
                 viewsets.GenericViewSet):
    # GenericViewSet:-   The GenericViewSet class does not provide any actions by default,
    # but does include the base set of generic view behavior, such as
    # the `get_object` and `get_queryset` methods.
    serializer_class = serializers.TagSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = models.Tag.objects.all()

    def get_queryset(self):
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            ),
        ]
    )
)
class IngredientViewsets(mixins.DestroyModelMixin,
                         mixins.ListModelMixin ,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):

    serializer_class = serializers.IngredientSerializer
    permission_classes =[IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = models.Ingredient.objects.all()

    def get_queryset(self):
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()