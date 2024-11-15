from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from shop.models import Category,Product
from django.http import HttpResponse
from django.contrib.auth import login,authenticate

# Create your views here.
def categories(request):
    c=Category.objects.all()
    context={'categories':c}
    return render(request,'categories.html',context)

def products(request,p):  #here p receives the category id
    print(p)
    c=Category.objects.get(id=p)   #reads a particular category object using id
    p=Product.objects.filter(category=c)  #reads all products under a particular category object
    context={'categories':c,'product':p}
    return render(request,'products.html',context)

def productdetails(request,p):
    pro=Product.objects.get(id=p)
    context={'product':pro}
    return render(request,'productdetails.html',context)

def register(request):
    if (request.method == "POST"):
        u = request.POST['u']
        p = request.POST['p']
        cp = request.POST['cp']
        f = request.POST['f']
        l = request.POST['l']
        e = request.POST['e']
        if (p == cp):
            u = User.objects.create_user(username=u, password=p, first_name=f, last_name=l, email=e)
            u.save()
            return redirect('shop:categories')
        else:
            return HttpResponse("Passwords are not same")
    return render(request,'register.html')

def user_login(request):
    if (request.method == "POST"):
        u = request.POST['u']
        p = request.POST['p']
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('shop:categories')
        else:
            return HttpResponse("Invalid Credentials")
    return render(request,'login.html')


def user_logout(request):
    user_logout(request)
    return redirect('shop:login')


def addcategories(request):
    if(request.method=="POST"):
        n=request.POST['n']
        i = request.FILES.get('i')
        d = request.POST['d']
        c=Category.objects.create(name=n,image=i,description=d)
        c.save()
        return redirect('shop:categories')
    return render(request,'addcategories.html')

def addproducts(request):
    if(request.method == "POST"):
        na = request.POST['na']
        im = request.FILES['im']
        de = request.POST['de']
        s = request.POST['s']
        p = request.POST['p']
        c = request.POST['cat']
        cat=Category.objects.get(name=c)

        p=Product.objects.create(name=na,image=im,description=de,stock=s,price=p,category=cat)
        p.save()
        return redirect('shop:categories')

    return render(request,'addproducts.html')


def addstock(request,p):
    p=Product.objects.get(id=p)
    if(request.method=="POST"):
        p.stock=request.POST['ad']
        p.save()
        return redirect('shop:categories')
    context={'pro':p}
    return render(request,'addstock.html',context)