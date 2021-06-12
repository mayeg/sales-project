from django.db import models


class Client(models.Model):
    document = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250, blank=True)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Bill(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=250)
    nit = models.CharField(max_length=20)
    code = models.CharField(max_length=3)

    def __str__(self):
        return self.company_name


class Product(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class BillProduct(models.Model):
    bill_id = models.ForeignKey(Bill, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
