import csv
import io

from django.db import connection
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sales.models import Client, Bill, Product, BillProduct
from sales.serializers.product_serializers import ProductSerializers
from rest_framework.permissions import IsAuthenticated


class ClientView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query = 'select * from sales_client sc'
        client_list = Client.objects.raw(query)
        client_response = []
        for client in client_list:
            client_response.append(self.__serialize_client(client))
        return Response(client_response)

    def post(self, request):
        data = request.data
        document = data.get('document')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        if data and document:
            query = f"select * from sales_client sc where sc.document = '{document}'"
            client_exist = Client.objects.raw(query)
            if client_exist:
                response_status = status.HTTP_400_BAD_REQUEST
                response = {"message": 'Ya existe un cliente con el documento'}
            elif document and first_name and email:
                new_client = Client(
                    document=document,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )
                new_client.save()
                response_status = status.HTTP_200_OK
                response = {"message": 'Cliente creado exitosamente'}
            else:
                response_status = status.HTTP_400_BAD_REQUEST
                response = {"message": 'Datos invalidos'}
        else:
            response_status = status.HTTP_400_BAD_REQUEST
            response = {"message": 'Documento es requerido'}

        return Response(response, status=response_status)

    def __serialize_client(self, client):
        return {
            "id": client.id,
            "document": client.document,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email": client.email
        }


class ClientDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, id):
        data = self.__validate_put_data(request.data)
        if not data:
            return Response({"message": 'Datos invalidos'}, status=status.HTTP_400_BAD_REQUEST)
        client_exist = Client.objects.get(id=id)
        if client_exist:
            client_exist.document = data["document"]
            client_exist.first_name = data["first_name"]
            client_exist.last_name = data["last_name"]
            client_exist.email = data["email"]
            client_exist.save()
            response_status = status.HTTP_200_OK
            response = {"message": 'Se actualiza el cliente'}
        else:
            response_status = status.HTTP_404_NOT_FOUND
            response = {"message": 'El cliente no existe'}

        return Response(response, status=response_status)

    def delete(self, request, id):
        client_exist = Client.objects.get(id=id)
        if client_exist:
            client_exist.delete()
            response_status = status.HTTP_200_OK
            response = {"message": 'Se ha eliminado el cliente'}
        elif not client_exist:
            response_status = status.HTTP_400_BAD_REQUEST
            response = {"message": 'No se encuentra el cliente'}
        else:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"message": 'Se ha presentado un error inesperado'}
        return Response(response, status=response_status)

    def __validate_put_data(self, data):
        document = data.get('document')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        if not document or not first_name or not last_name or not email:
            return None
        return {
            "document": document,
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        }


class ProductView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Product.objects.all()
        serializer = ProductSerializers(queryset, many=True).data
        return Response(serializer)

    def post(self, request):
        data = self.__validate_post_data(request.data)
        if not data:
            response = {"message": 'Nombre es requerido'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        exist_product = Product.objects.filter(name=data['name'])
        if exist_product:
            response = {"message": 'Ya existe un producto con ese nombre'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        new_product = Product(
            name=data['name'],
            description=data['description']
        )
        new_product.save()
        response = {"message": 'Producto Creado'}
        return Response(response)

    def __validate_post_data(self, data):
        name = data.get('name')
        description = data.get('description')
        if not name:
            return None
        return {
            "name": name,
            "description": description
        }


class ProductDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, id):
        data = self.__validate_put_data(request.data)
        if not data:
            response = {"message": 'Nombre es requerido'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        product_exist = Product.objects.filter(id=id).first()
        if product_exist:
            product_exist.name = data['name']
            product_exist.description = data['description']
            product_exist.save()
            response = {"message": 'Producto Actualizado'}
            response_status = status.HTTP_200_OK
        else:
            response = {"message": 'No se encuentra el producto'}
            response_status = status.HTTP_400_BAD_REQUEST
        return Response(response, status=response_status)

    def delete(self, request, id):
        product_exist = Product.objects.filter(id=id).first()
        if product_exist:
            product_exist.delete()
            response_status = status.HTTP_200_OK
            response = {"message": 'Se ha eliminado el producto'}
        elif not product_exist:
            response_status = status.HTTP_400_BAD_REQUEST
            response = {"message": 'No se encuentra el producto'}
        else:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"message": 'Se ha presentado un error inesperado'}
        return Response(response, status=response_status)

    def __validate_put_data(self, data):
        name = data.get('name')
        description = data.get('description')
        if not name:
            return None

        return {
            "name": name,
            "description": description
        }


class BillView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        bills_response = []
        query = """select sb.id, sb.company_name, sb.nit, sb.code, sc.id as client_id, sc.document, sc.first_name, 
        sc.last_name, sc.email
         from sales_bill sb left join sales_client sc on sc.id = sb.client_id"""
        with connection.cursor() as connection_cursor:
            connection_cursor.execute(query)
            for row in connection_cursor.fetchall():
                bill = self.__serialize_bill(row)
                sql = f"""select sp.*
                 from sales_product sp 
                 left join sales_billproduct sbp on sp.id = sbp.product_id_id
                 where sbp.bill_id_id = {bill['id']}"""
                connection_cursor.execute(sql)
                products_bill = connection_cursor.fetchall()
                products = []
                for product in products_bill:
                    products.append({
                        "name": product[0],
                        "description": product[1]
                    })
                bill['products'] = products
                bills_response.append(bill)
        return Response(bills_response)

    def post(self, request):
        data = self.__validate_post_data(request.data)
        if not data:
            response = {"message": 'Datos invalidos'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        client_exist = Client.objects.get(id=data['client_id'])
        if client_exist:
            new_bill = Bill(
                company_name=data['company_name'],
                nit=data['nit'],
                code=data['code'],
                client_id=data['client_id'],
            )
            new_bill.save()
            data['bill_id'] = new_bill.id
            self.__create_bill_product(data)
            response_status = status.HTTP_200_OK
            response = {"message": 'Factura creada con exito'}
        else:
            response_status = status.HTTP_400_BAD_REQUEST
            response = {"message": 'El cliente no existe'}
        return Response(response, status=response_status)

    def __create_bill_product(self, data):
        for product_id in data['products']:
            new_bill_product = BillProduct(
                bill_id_id=data['bill_id'],
                product_id_id=product_id,
            )
            new_bill_product.save()

    def __validate_products(self, products_ids):
        for product in products_ids:
            product_exist = Product.objects.filter(id=product).first()
            if not product_exist:
                return False
        return True

    def __validate_post_data(self, data):
        company_name = data.get('company_name')
        nit = data.get('nit')
        code = data.get('code')
        client_id = data.get('client_id')
        products = data.get('products')
        if not company_name or not nit or not code or not client_id:
            return None
        if self.__validate_products(products):
            return {
                "company_name": company_name,
                "nit": nit,
                "code": code,
                "client_id": client_id,
                "products": products
            }
        return None

    def __serialize_bill(self, row):
        return {
            "id": row[0],
            "company_name": row[1],
            "nit": row[2],
            "code": row[3],
            "client": {
                "id": row[4],
                "document": row[5],
                "first_name": row[6],
                "last_name": row[7],
                "email": row[8]
            },
            "products": []
        }


class BillDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, id):
        data = self.__validate_put_data(request.data)
        if not data:
            return Response({"message": 'Datos invalidos'}, status=status.HTTP_400_BAD_REQUEST)
        bill_exist = Bill.objects.filter(id=id).first()
        if bill_exist:
            bill_exist.company_name = data["company_name"]
            bill_exist.nit = data["nit"]
            bill_exist.code = data["code"]
            bill_exist.client_id = data["client_id"]
            bill_exist.save()
            data['bill_id'] = bill_exist.id
            self.__update_bill_product(data)
            response_status = status.HTTP_200_OK
            response = {"message": 'Se actualiza la factura'}
        else:
            response_status = status.HTTP_404_NOT_FOUND
            response = {"message": 'La factura no existe'}

        return Response(response, status=response_status)

    def delete(self, request, id):
        bill_exist = Bill.objects.filter(id=id).first()
        if bill_exist:
            bill_exist.delete()
            response_status = status.HTTP_200_OK
            response = {"message": 'Se ha eliminado la factura'}
        elif not bill_exist:
            response_status = status.HTTP_400_BAD_REQUEST
            response = {"message": 'No se encuentra la factura'}
        else:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response = {"message": 'Se ha presentado un error inesperado'}
        return Response(response, status=response_status)

    def __update_bill_product(self, data):
        bill_product_exist = BillProduct.objects.filter(bill_id_id=data['bill_id']).first()
        for product_id in data['products']:
            bill_product_exist.product_id_id = product_id
            bill_product_exist.save()

    def __validate_products(self, products_ids):
        for product in products_ids:
            product_exist = Product.objects.get(id=product)
            if not product_exist:
                return False
        return True

    def __validate_put_data(self, data):
        company_name = data.get('company_name')
        nit = data.get('nit')
        code = data.get('code')
        client_id = data.get('client_id')
        products = data.get('products')
        if not company_name or not nit or not code or not client_id:
            return None
        if self.__validate_products(products):
            return {
                "company_name": company_name,
                "nit": nit,
                "code": code,
                "client_id": client_id,
                "products": products
            }
        return None


class ClientExportView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="clientes.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Documento', 'Nombre completo ', 'Cantidad facturas'])
        sql = """select sc.document, sc.first_name, sc.last_name, count(sb.client_id) as client_bill
	                from sales_client sc left join sales_bill sb on sc.id = sb.client_id 
	                group by sc.document, sc.first_name, sc.last_name"""
        with connection.cursor() as connection_cursor:
            connection_cursor.execute(sql)
            for row in connection_cursor.fetchall():
                writer.writerow(self.__format_client(row))

        return response

    def __format_client(self, row):
        return row[0], f"{row[1]} {row[2]}", row[3]


class ClientImportView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        success_client = 0
        error_client = 0
        clients_exists = 0

        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            response = {"message": "El formato del archivo es invalido, deber csv"}
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(response, status=status_code)
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        # next(io_string)
        for row in csv.reader(io_string, delimiter=';', quotechar="|"):
            print(row)
            if not Client.objects.filter(document=row[0]).first():
                if row[0] and row[1] and row[3]:
                    new_client = Client(
                        document=row[0],
                        first_name=row[1],
                        last_name=row[2],
                        email=row[3]
                    )
                    new_client.save()
                    success_client += 1
                else:
                    error_client += 1
            else:
                clients_exists += 1

        response = {"message": f"Clientes agregados:{success_client}, Clientes con falta de datos:{error_client},"
                              f"clientes que ya existian: {clients_exists}"}
        if error_client > 0 or clients_exists > 0:
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_200_OK

        return Response(response, status=status_code)

