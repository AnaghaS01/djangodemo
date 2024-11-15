from django.shortcuts import render,redirect
from shop.models import Product
from cart.models import Cart
from django.contrib.auth.decorators import login_required
import razorpay
from cart.models import Payment,Order_details,User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
# Create your views here.
@login_required

def addtocart(request,i):
    p=Product.objects.get(id=i)
    u=request.user
    try:  #if
        c=Cart.objects.get(product=p,user=u)  #checks the product present in cart table for a particular user
        if(p.stock>0):
            c.quantity+=1  #if present it will increment the quantity of product
            c.save()
            p.stock-=1
            p.save()
    except:
        c=Cart.objects.create(product=p,user=u,quantity=1)
        if (p.stock > 0):
            c.save()
            p.stock -= 1
            p.save()
    return redirect('cart:cart')

@login_required
def cartview(request):
    u=request.user
    try:
        c=Cart.objects.filter(user=u)  #all cart items for a particular user
        total=0
        for i in c:
            total+=i.quantity*i.product.price
    except:
        pass
    context={'cart':c,'total':total}
    return render(request,'cart.html',context)

@login_required
def cartremove(request,i):
    p = Product.objects.get(id=i)
    u = request.user
    try:  # if
        c = Cart.objects.get(product=p, user=u)
        if (c.quantity > 1):
            c.quantity -= 1
            c.save()
            p.stock += 1
            p.save()
        else:
            c.delete()
            p.stock += 1
            p.save()
    except:
        pass
    return redirect('cart:cart')

@login_required
def cartdelete(request,i):
    p = Product.objects.get(id=i)
    u = request.user
    try:  # if
        c = Cart.objects.get(product=p, user=u)
        c.delete()
        p.stock += c.quantity
        p.save()
    except:
        pass
    return redirect('cart:cart')


def orderform(request):
    if(request.method=="POST"):
        address=request.POST['a']
        phone=request.POST['ph']
        pin=request.POST['p']
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total+=i.quantity*i.product.price
        total1=int(total*100)
        client=razorpay.Client(auth=('rzp_test_swLgJlOG1Uhdoe','pWYsZ7oT051zRzgWhJFoeagU')) #creates a client connection using razorpay id and secret code
        response_payment=client.order.create(dict(amount=total1,currency="INR"))  #creates an order with razorpay using razorpay client
        print(response_payment)
        order_id=response_payment['id']
        status=response_payment['status']

        if(status=="created"):
            p=Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c:
                o=Order_details.objects.create(product=i.product,user=u,no_of_items=i.quantity,address=address,phone=phone,pin=pin,order_id=order_id)
                o.save()
        response_payment['name']=u.username

        context={'payment':response_payment}
        return render(request,'payment.html',context)

    return render(request,'order.html')
@csrf_exempt

def paymentstatus(request,u):
    u = User.objects.get(username=u)
    if not request.user.is_authenticated:
        login(request,u)
    if(request.method=="POST"):
        response=request.POST
        print(response)
        param_dict={
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature'],
        }  #To check the authenticity of razorpay signature
        client = razorpay.Client(auth=('rzp_test_swLgJlOG1Uhdoe', 'pWYsZ7oT051zRzgWhJFoeagU'))
        print(client)
        try:
            status=client.utility.verify_payment_signature(param_dict)
            print(status)  #To retrieve a particular record from payment table matching with razorpay response order id
            p=Payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id=response['razorpay_payment_id']
            p.paid=True
            p.save()  #To retrieve a record from Order_details table matching with razorpay response order id
            o=Order_details.objects.filter(order_id=response['razorpay_order_id'])
            for i in o:
                i.payment_status="completed"
                i.save()
            c=Cart.objects.filter(user=u)
            c.delete()
        except:
            pass
    return render(request,'paymentstatus.html',{'status':status})

@login_required
def orderview(request):
    u=request.user
    o=Order_details.objects.filter(user=u)
    print(o)
    context={'orders':o}
    return render(request,'orderview.html',context)


