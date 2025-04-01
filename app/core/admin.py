from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUser
from django.utils.translation import gettext_lazy as _
from . import models



class UserAdmin(BaseUser):
    ordering = ['id']
    list_display =['email', 'name']
    fieldsets =(
        (None ,{'fields':('email' , 'password')}),
        (
            _('Permissions') ,
            {
                'fields':(
                    'is_active' ,
                    'is_superuser' ,
                    'is_staff'
                )
            }
        ),
        (_('Important Dates') ,{'fields' :('last_login',)}),
    )
    readonly_fields =['last_login']
    add_fieldsets=(
        (None ,{
            "classes":('wide',),
            "fields":(
                'email' ,
                'password',
                'password1',
                'name',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
    )
admin.site.register(models.User,UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)