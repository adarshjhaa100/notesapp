from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import Permission
from cryptography.fernet import Fernet

key=b'9EeYD0sGXifuEwC1a_y-jRWaB0iAGqiE9_BPW4N4vq0=' 
             #this is your "password"
print(key)
cipher_suite = Fernet(key)

# Endpoint for creating a user
@csrf_exempt
def createUser(request):
    
    if(request.method=='POST'):
        details=json.loads(request.body)
        try:
            obj=User.objects.get(username=details['username'])
            return JsonResponse({
                'status':'account already exists'
            })
        except User.DoesNotExist:    
            user=User.objects.create_user(
                username=details['username'],
                password=details['password'],)

            # Adding permissions to add and view note
            perm=Permission.objects.get(name='Can add note')
            user.user_permissions.add(perm)
            perm=Permission.objects.get(name='Can view note')
            user.user_permissions.add(perm)
            
            user.save()

            return JsonResponse({
                'status':'account creation success'
            })  

    return JsonResponse({
        'status':'GET request not allowed'
    })


# Handling User login
@csrf_exempt
def loginUser(request):
    if(request.method=='POST'):
        details=json.loads(request.body)
        username = details['username']
        password = details['password']
        # print(details)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request,user)
            # print(user.is_authenticated)
            return JsonResponse({
                'status':'success',
                'userId':user.id
            })
        
        return JsonResponse(
            {
                'status':'failed login'
            })
    return JsonResponse(
            {
                'status':'GET method not Allowed'
            })

# Viewing the notes for each user
def listUserNotes(request):
    # print(request.GET['userId'])
    userId=request.GET['userId']
    
    try:
        user=User.objects.get(id=userId)
    
        if user.is_authenticated:
            key=b'9EeYD0sGXifuEwC1a_y-jRWaB0iAGqiE9_BPW4N4vq0=' 
            # print(user.note_set.all())
            # cipher_suite.decrypt(

            notes=[cipher_suite.decrypt(eval(i.content)).decode() for i in user.note_set.all() ]
            return JsonResponse(
            {   
                'status':'success',
                'notes':notes
            })
        return JsonResponse(
        {
            'status':'user is not logged in'
        })       
    except User.DoesNotExist:
        return JsonResponse(
            {
                'status':'user does not exist'
            })


# Method for adding notes endpoint
@csrf_exempt
def addNotes(request):
    if(request.method=='POST'):
        userId=json.loads(request.body)['userId']
        try:
            user=User.objects.get(id=userId)
        
            if user.is_authenticated:
                content=json.loads(request.body)['note']
               
                
                encoded_text = cipher_suite.encrypt(str(content).encode())
                decoded_text = cipher_suite.decrypt(encoded_text)
                user.note_set.create(content=encoded_text)
                return JsonResponse({'status':'success'})

            return JsonResponse({'status':'user not logged in'})
        except User.DoesNotExist:
            return JsonResponse(
                {
                    'status':'user does not exist'
                })
