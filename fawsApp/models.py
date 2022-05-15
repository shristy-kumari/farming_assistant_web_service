from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.fields import AutoField
# Create your models here.

gender_choice = (
    ('m', 'Male'),
    ('f', 'Female'),
)


class Role(models.Model):
    Role = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'Role'

    def __str__(self):
        return self.Role
        
class Master(models.Model):
    Role = models.ForeignKey(Role, on_delete=models.CASCADE)
    Email = models.EmailField(max_length=50, unique=True)
    Password = models.CharField(max_length=50)
    IsActive = models.BooleanField(default=False)
    DateCreated = models.DateTimeField(auto_now_add=True)
    DateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Master'

    def __str__(self):
        return self.Email


class Seller(models.Model):
    Master = models.ForeignKey(Master, on_delete=models.CASCADE) # for user and supplier
    Image = models.FileField(upload_to="seller/profile_img/", default="default.png")
    FullName = models.CharField(max_length=50, default='')
    Mobile = models.CharField(max_length=10, default='')
    Gender = models.CharField(max_length=50, choices=gender_choice)
    Address = models.TextField(max_length=50, default='')
    Country = models.CharField(max_length=20, default='')
    State = models.CharField(max_length=20, default='')
    City = models.CharField(max_length=20, default='')
    Pincode = models.CharField(max_length=6, default='')

    IsActive = models.BooleanField(default=False)  

    class Meta:
        db_table = 'Seller'

    def __str__(self):
        return 'No Details' if not self.FullName else self.FullName

class Farmer(models.Model):
    Master = models.ForeignKey(Master,on_delete=models.CASCADE)
    Image = models.FileField(upload_to="farmer/profile_img/", default="default.png")
    FullName = models.CharField(max_length=50, default='')
    Mobile = models.CharField(max_length=10, default='')
    Gender = models.CharField(max_length=50, choices=gender_choice)
    Address = models.TextField(max_length=50, default='')
    Country = models.CharField(max_length=20, default='')
    State = models.CharField(max_length=20, default='')
    City = models.CharField(max_length=20, default='')
    Pincode = models.CharField(max_length=6, default='')

    IsActive = models.BooleanField(default=False)  

    class Meta:
        db_table = 'Farmer'

    def __str__(self):
        return 'No Details' if not self.FullName else self.FullName




#######################################




product_categories = {
    'Vegitable_seeds': [],
    'Flower_seeds': [],
    'Fruits_seeds': [],
    'Hybrid_seeds': [],
    'Herbs_seeds': [],
    'Forestry_Tree seeds': [],
    'Chemical_fertilizers': [],
    'Gardening_Tools': []

}
product_categories_choices = []
for t in product_categories.keys():
    product_categories_choices.append( (t, t.capitalize()) )

Product_categories_choices = tuple(product_categories_choices)


product_unit = {
    '50Kg': [],
    '1Kg': [],
    '500g': [],
    '200g': [],
    '100g': [],
    '50g': [],
    '25g': [],
    '10g': [],
    '5g': [],
    '1Ltr': [],
    '500ML': [],
    '200M': [],
    '100ML': [],
    'Piece': []
}
product_unit_choices = []
for t in product_unit.keys():
    product_unit_choices.append( (t, t.capitalize()) )

Product_unit_choices = tuple(product_unit_choices)


class Product(models.Model):
    Seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    Image = models.FileField(upload_to="seller/products/", default="default.png")
    Categories = models.CharField(max_length=50, choices=product_categories_choices)
    Name = models.CharField(max_length=50, default='')
    Unit = models.CharField(max_length=5, choices=product_unit_choices)
    Price = models.DecimalField(max_digits=8, decimal_places=2)
    DateTime = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'Product'

    def __str__(self):
        return self.Name
   

class Cart(models.Model):
    Farmer = models.ForeignKey(Farmer,on_delete=models.CASCADE)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Quantity = models.IntegerField(default=1)
    Total = models.DecimalField(max_digits=8, decimal_places=2)
    DateTime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Cart"
        
    def __str__(self):
        return self.Product.Name

class CheckOut(models.Model):
    Master = models.ForeignKey(Master, on_delete=models.CASCADE) # for farmer
    Shipping_Name = models.CharField(max_length=20,default='')
    Phone_Number = models.IntegerField()
    House_Number = models.IntegerField()
    Floor_Number = models.IntegerField()
    Country = models.CharField(max_length=20, default='')
    State = models.CharField(max_length=15,default='')
    City = models.CharField(max_length=15 ,default='')
    Area = models.CharField(max_length=20,default='')
    Address = models.CharField(max_length=40, default='')
    Pincode = models.IntegerField()
    DateTime = models.DateTimeField(auto_now=True)


class Order(models.Model):
    Farmer = models.ForeignKey(Farmer,on_delete=models.CASCADE)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Quantity = models.IntegerField(default=1)
    Total = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        db_table = "Order"
        
    def __str__(self):
        return self.Product.Name
   
   
    

class Transaction(models.Model):
    made_by = models.CharField(max_length=10)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)

class Feedback(models.Model):
    Master = models.ForeignKey(Master, on_delete=models.CASCADE)
    Farmer = models.ForeignKey(Farmer,on_delete=models.CASCADE)
    Name = models.CharField(max_length=50)
    Email = models.EmailField(max_length=50)
    Review = models.CharField(max_length=2000)

    class Meta:
        db_table = 'Feedback'





