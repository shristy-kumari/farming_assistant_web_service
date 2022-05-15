from django.contrib import admin

# Register your models here.
from .views import app_info
from .models import *

class SuperAdmin(admin.ModelAdmin):
    admin.site.site_header = admin.site.site_title = app_info['app_name']
    admin.site.index_title = f"{app_info['app_name']}'s Admin"
    empty_value_display = '-empty-'
    list_per_page = 10

class RoleAdmin(admin.ModelAdmin):
    list_display = list_display_links = ('id', 'Role')
    list_filter = list_display
    
    
class MasterAdmin(admin.ModelAdmin):
    list_display = list_display_links = ('id', 'Email', 'Role', 'IsActive')
    list_filter = ('Role', 'IsActive')
    
class ProductAdmin(admin.ModelAdmin):
    list_display = list_display_links = ('Seller','DateTime')
    list_filter = list_display
    
class CartAdmin(admin.ModelAdmin):
    list_display = list_display_links = ('id', 'Name')
    list_filter = list_display
    
models_list = [  Seller, Farmer, CheckOut, Feedback, Cart, Order, Transaction]
roles = ['seller','farmer']
if not len(Role.objects.all()):
    for role in roles:
        Role.objects.create(Role=role)
        
for model in models_list:
    admin.site.register(model, SuperAdmin)

admin.site.register(Role, RoleAdmin)
admin.site.register(Master, MasterAdmin)
admin.site.register(Product, ProductAdmin)

