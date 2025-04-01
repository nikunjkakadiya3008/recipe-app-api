from django.urls import path , include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'recipes' , views.RecipeViewsets)
router.register(r'tags' , views.TagViewSet)
router.register(r'ingredients' , views.IngredientViewsets)
app_name = 'recipe'

urlpatterns = [
    path('' , include(router.urls)),
]
