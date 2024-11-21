from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, JsonResponse
from .models import Category, CategoryForm, Product, ProductForm
from django.views import View
import json
from django.core.cache import cache
import time
import random
from django.utils import timezone
from faker import Faker
from django.test import RequestFactory
from django.urls import reverse
# Create your views here.

def index(request):
    return render(request, 'index.html')

class ProductView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            print(data['category_name'])
            category = Category.objects.get(id=data['category_name'])          
            data['category'] = category
            form = ProductForm(data)

            if form.is_valid():
                print('valid form')
                product = form.save()
                products = Product.objects.all()
                resetCache('products')

            return redirect('/products')
            
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


    def get(self, request, id=None):
        # p = Product.objects.all()
        # p.delete()
        # insertData()
        if id!=None:
            
            products = Product.objects.get(id=id)
            categories = getSetCache('categories', Category)
            context = {
                'active_tab': 'products',
                'product': products,
                'categories' : categories
            }
            return render(request, 'product_detail.html', context)
        else:
            last = time.time()
            category_name = request.GET.get('category_name')
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')

            products = getSetCache('products', Product)
 
            if category_name:
                category = Category.objects.get(name=category_name)
                products = getSetCache('products', Product, category)

            if not min_price:
                min_price = 0
            
            if not max_price:
                max_price = 9999999999

            try:
                products = products.filter(price__range=(float(min_price), float(max_price)))
            except ValueError:
                pass 

            categories = getSetCache('categories', Category)

            context = {
                'active_tab': 'products', 
                'products': products,  
                'categories': categories,
            }
            print(time.time()-last)
            return render(request, 'products_list.html', context)
        

    def delete(self, request, id=None):
        try:
            product = Product.objects.get(id=id)  
            category = product.category
            product.delete()

            resetCache('products')
            resetCache(f'products?category={category}')
            factory = RequestFactory()
            url = reverse('products-list')
            request = factory.get(url)

            viewInstance = ProductView.as_view()

            response = viewInstance(request)

            return response
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    def put(self, request, id=None):
        try:
            product = Product.objects.get(id=id)

            data = json.loads(request.body)

            category = Category.objects.get(id=data['category_name'])
            product.name = data['name']
            product.description = data['description']
            product.price = data['price']
            product.category = category
            product.save() 
            resetCache('products')
            
            categories = getSetCache('categories', Category)
            return redirect(reverse('products-detail', args=[id]))
        
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)


class CategoryView(View):
    def get(self, request, id=None):
        if id != None:
            category = Category.objects.get(id=id)
            context = {
                'category' : category
            }
            return render(request, 'category_detail.html', context)
        else:
            categories = getSetCache('categories', Category)
            context = {
                'active_tab': 'categories',
                'categories': categories, 
            }

            return render(request, 'categories_list.html', context)
        
    def post(self, request):
        try:

            data = json.loads(request.body)

            category = Category.objects.create(
                name=data['name'],
                description=data['description']
            )
            print("New category created")

            categories = Category.objects.all()

            resetCache('categories')

            return redirect('/categories/')

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    def put(self, request, id=None):
        category = Category.objects.get(id=id)

        updated_data = json.loads(request.body)

        category.name = updated_data['name']
        category.description = updated_data['description']
        category.save() 

        categories = Category.objects.all()
        resetCache('categories')

        context = {
            'name' : category.name,
            'description' : category.description
        }

        return render(request, 'category_detail.html', context)

    def delete(self, request, id=None):
        print(id)
        category = Category.objects.get(id=id) 
        category.delete()

        categories = Category.objects.all() 
        resetCache('categories')
        context = {
            'active_tab': 'categories',
            'categories': categories, 
        }

        return render(request, 'categories_list.html', context)
    
timeout = 60 * 5
def getSetCache(key, model, category=None):
    print('========')
    if category:
        result = cache.get(f"{key}?category={category.name}")
        if result:
            print('ada result')
            return result
        else:
            data = model.objects.all()
            data = data.filter(category=category.id)
            cache.set(f"{key}?category={category.name}", data, timeout)
            return data
    else:
        result = cache.get(key)
        if result:
            print('ada result')
            return result
        else:
            data = model.objects.all()
            cache.set(f"{key}", data, timeout)
            return data

def resetCache(key):
    cache.delete(key)       


def insertData():

    fake = Faker()


    novel_category, created = Category.objects.get_or_create(name="novel")
    book_category, created = Category.objects.get_or_create(name="book")


    used_names = set()


    for i in range(900):

        category = random.choice([novel_category, book_category])
        
        name = fake.unique.word()
        while name in used_names:
            name = fake.unique.word()
        
        used_names.add(name)
        
        description = fake.text(max_nb_chars=200)
        price = round(random.uniform(5.0, 100.0), 2) 
        
        now = timezone.now()

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
            created_at=now,
            updated_at=now
        )
        print(i)

    print("Successfully created 1000 products.")

    