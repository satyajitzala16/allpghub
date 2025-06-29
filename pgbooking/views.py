import random
import razorpay
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse,redirect,get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Author,Amenity,userregister,category,room,UserProfile,citytable,Page,VideoPage,PagePhoto,Feedback,ownerregistration,addpg,Breakfast, Lunch, Dinner, WeeklyMealPlan,Comment,RoomRating,Like,PGImage
from.import views
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg

from django.utils.decorators import method_decorator

# Create your views here.


# Initialize Razorpay client



# index page view 
def index(request):
    if 'email' in request.session:
        catdata = category.objects.all()
        page_photos = PagePhoto.objects.all()  # Fetch all PagePhoto objects
        videos = list(VideoPage.objects.all())  # Fetch all VideoPage objects and convert to list
        random.shuffle(videos)  # Randomize the order of videos
        return render(request, 'index.html', {'cat': catdata, 'session': True, 'page_photos': page_photos, 'videos': videos})
    else:
        catdata = category.objects.all()
        page_photos = PagePhoto.objects.all()  # Fetch all PagePhoto objects
        videos = list(VideoPage.objects.all())  # Fetch all VideoPage objects and convert to list
        random.shuffle(videos)  # Randomize the order of videos
        return render(request, 'index.html', {'cat': catdata, 'page_photos': page_photos, 'videos': videos})   

# example allroom view
def allroom(request):    
    prodata = room.objects.all()
    return render(request,'room.html',{'pro':prodata})

# user login view
def login(request):
    if request.method == 'POST':
        try:
            user = userregister.objects.get(email = request.POST['email'])
            
            if user.password == request.POST['password']:
                request.session['email'] = user.email
                return redirect('index')
            else:
                return  render(request, 'login.html',{'pass':"password is invalid"})  
            #    return render(request, 'login.html')
        except:  
            return  render(request, 'login.html',{'notregstered':"before login you have to registere first.."})            
    else: 
        return render(request, 'login.html')


def send_otp(email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP code is: {otp}"
    from_email = 'allpghub@gmail.com'  # Replace with your email
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)

def register(request):
    if request.method == 'POST':
        user = userregister()
        user.name = request.POST['name']
        user.email = request.POST['email']
        user.add = request.POST['add']
        user.password = request.POST['password']
        user.mob = request.POST['mob']
        
        # Check if email is already registered
        useralready = userregister.objects.filter(email=request.POST['email']).first()
        if useralready:
            return render(request, 'register.html', {'already': "This email is already registered"})
        else:
            # Check if passwords match
           if request.POST['password'] == request.POST['cp']:
                otp = random.randint(100000, 999999)  # Generates a random 6-digit OTP
                user.otp = str(otp)  # Store OTP as a string
                user.save()  # Save the user instance with the OTP
                send_otp(user.email, otp)  # Send OTP to the user's email
                
                return render(request, 'otp_verification.html', {'email': user.email})  # Pass email to the verification page
           else:
                return render(request, 'register.html', {'pass': "Passwords did not match..."})
    else:
        return render(request, 'register.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp'].strip()  # Trim spaces
        email = request.POST['email']

        # Get the user by email
        user = userregister.objects.filter(email=email).first()

        if user is None:  # Check if the user exists
            return render(request, 'otp_verification.html', {'error': 'User not found', 'email': email})

        print(f"Entered OTP: {entered_otp}")  # Debug: print entered OTP
        print(f"Stored OTP: {user.otp}")      # Debug: print stored OTP

        if str(user.otp) == entered_otp:
            # OTP is correct, redirect to login
            user.otp = None  # Clear the OTP once verified
            user.save()
            return render(request, 'login.html')
        else:
            return render(request, 'otp_verification.html', {'error': 'Invalid OTP', 'email': email})
    else:
        return redirect('register')


from datetime import timedelta
from django.conf import settings
from django.shortcuts import redirect

# In settings.py
SESSION_COOKIE_AGE = 48 * 60 * 60  # 48 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Optional: Expires when the browser closes

def logout(request):
    # Clear the email from the session
    if 'email' in request.session:
        del request.session['email']
    return redirect('index')  
    
def about_us(request):
    return render(request,'aboutus.html')

def contact_us(request):
    return render(request,'contact.html')

#one by one pg show catpro view
from django.db.models import Avg


def rate_room(request, room_id):
    if request.method == "POST" and 'email' in request.session:
        rating_value = int(request.POST.get('rating', 0))
        comment_value = request.POST.get('comment', '')

        # Fetch room and user instances
        room_instance = get_object_or_404(room, id=room_id)
        user_instance = get_object_or_404(userregister, email=request.session['email'])

        # Check if the user already rated this room
        rating, created = RoomRating.objects.get_or_create(
            room=room_instance,
            user=user_instance,
            defaults={'rating': rating_value, 'comment': comment_value}
        )
        
        if not created:
            # Update the existing rating
            rating.rating = rating_value
            rating.comment = comment_value
            rating.save()

        return redirect('catpro', pgname=room_instance.pgname)

def catpro(request, pgname):
    ac_filter = request.GET.get('ac_type', 'all')

    # Get PG details and related images
    pg_details = addpg.objects.filter(pgname=pgname).first()
    pg_images = PGImage.objects.filter(pg=pg_details) if pg_details else []

    if ac_filter == 'AC':
        rooms = room.objects.filter(pgname=pgname, ac_type='AC')
    elif ac_filter == 'Non-AC':
        rooms = room.objects.filter(pgname=pgname, ac_type='Non-AC')
    else:
        rooms = room.objects.filter(pgname=pgname)

    # Add average rating and rating count for each room
    for room_instance in rooms:
        room_ratings = room_instance.ratings.all()
        room_instance.average_rating = room_ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        room_instance.rating_count = room_ratings.count()

    session_active = 'email' in request.session

    # Split amenities into a list
    amenities = pg_details.amenities.split(',') if pg_details and pg_details.amenities else []

    return render(request, 'catpro.html', {
        'rooms': rooms,
        'pgname': pgname,
        'pgvideo': pg_details.pgvideo.url if pg_details and pg_details.pgvideo else None,
        'pg_images': pg_images,
        'session': session_active,
        'ac_filter': ac_filter,
        'amenities': amenities,  # Pass amenities to the template
    })


def booking(request, id):
    if 'email' not in request.session:
        return redirect('login')  # Redirect to login if not logged in

    if request.method == 'POST':
        email = request.session.get('email')

        # Check if the user has already booked a bed
        existing_booking = UserProfile.objects.filter(email=email).first()
        if existing_booking:
            messages.warning(request, "You have already booked a bed with this email.")
            return redirect('error_page')

        # Fetch room data
        try:
            room_instance = room.objects.get(id=id)
        except room.DoesNotExist:
            messages.error(request, "Room not found.")
            return redirect('index')

        # Get room type and number of beds booked from the form
        room_type = request.POST.get('room_type')
        beds_booked = int(request.POST.get('beds_booked', 1))

        # Check bed availability
        if room_type == 'single sharing' and beds_booked > 1:
            messages.error(request, "Only 1 bed can be booked for single sharing rooms.")
            return redirect('index')
        elif room_instance.bad_qty < beds_booked:
            messages.error(request, "Not enough beds available.")
            return redirect('index')

        # Calculate total price based on the number of beds booked
        total_price = int(room_instance.price) * beds_booked

        # Save booking details
        try:
            user_profile = UserProfile.objects.create(
                full_name=request.POST.get('fullname'),
                email=email,
                phone_number=request.POST.get('phone'),
                location=request.POST.get('location'),
                gender=request.POST.get('gender'),
                room_type=room_type,
                aadhaar_photo=request.FILES.get('aadhaarphoto'),
                personal_photo=request.FILES.get('personalphoto'),
                datetime=timezone.now(),
                room_price=total_price,  # Store the total price in the UserProfile
                pgname=room_instance.pgname,  # Store PG name in the UserProfile
            )

            # Update bed quantity
            room_instance.bad_qty -= beds_booked
            room_instance.save()

            messages.success(request, "Booking successful!")

            # Redirect to the user PDF page with the newly created user profile ID
            return redirect('user_pdf', user_id=user_profile.id)

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('error_page')  # General error handling

    return render(request, 'booking.html')
    
def booking_confirmation(request):
    return render(request, 'booking_confirmation.html')  # Render confirmation page

def error_page(request):
    return render(request, 'error_page.html')  # Render error page

#exmple admin page 
def admin(request):
    return render(request,'admin.html')

#user and owner are the perform forget password
def forget(request):
    return render(request,'forget.html')    


# user show particular one room deatil show
def prodetails(request,id):
    if 'email' in request.session: 
        pro = room.objects.get(pk = id)
        return render(request, 'prodetails.html',{'pro':pro,'session':True})
    else:
        pro = room.objects.get(pk = id)
        return render(request, 'prodetails.html',{'pro':pro})

def gender(request, gender):
    # Get all PGs filtered by gender
    pg_list = addpg.objects.filter(gender=gender,approved = True)
    # Get distinct cities for the selected gender
    cities = addpg.objects.filter(gender=gender,approved =True).values_list(
        'city', flat=True).distinct()
    return render(request, 'city.html', {'pg_list': pg_list, 'cities': cities, 'gender': gender})

from math import radians, sin, cos, sqrt, atan2
from django.shortcuts import render
import random

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def city(request, gender):
    selected_city = request.GET.get('city', '')
    selected_area = request.GET.get('area', '')
    search_query = request.GET.get('search', '').strip()
    selected_radius = request.GET.get('radius', '5')  # Default 5km radius
    
    # Base queryset
    queryset = addpg.objects.filter(gender=gender, approved=True).order_by('pgname')
    
    if selected_city:
        queryset = queryset.filter(city=selected_city)
        
        if selected_area:
            queryset = queryset.filter(area=selected_area)
            
            # Get the area coordinates
            area_pg = queryset.first()
            if area_pg and area_pg.arealatitude and area_pg.arealongitude:
                area_lat = float(area_pg.arealatitude)
                area_lon = float(area_pg.arealongitude)
            else:
                area_lat = None
                area_lon = None
            
            # Calculate distances for all PGs in the area
            pg_list = []
            radius_km = float(selected_radius)
            
            for pg in queryset:
                if pg.latitude and pg.longitude and area_lat is not None and area_lon is not None:
                    distance = haversine(
                        area_lat, 
                        area_lon,
                        float(pg.latitude),
                        float(pg.longitude)
                    )
                    pg.distance = round(distance, 2)
                    if distance <= radius_km:
                        pg_list.append(pg)
                else:
                    # Include PGs without coordinates
                    pg.distance = None
                    pg_list.append(pg)
        else:
            # City selected but no area - show all PGs in city
            pg_list = list(queryset)
            for pg in pg_list:
                pg.distance = None
    else:
        # No city selected - show all PGs for gender
        pg_list = list(queryset)
        for pg in pg_list:
            pg.distance = None
    
    # Apply search query filter if present
    if search_query:
        pg_list = [pg for pg in pg_list if search_query.lower() in pg.pgname.lower()]
    
    # Shuffle the PG listings randomly
    random.shuffle(pg_list)
    
    # Fetch unique cities and areas for dropdowns
    cities = addpg.objects.filter(gender=gender, approved=True).values_list('city', flat=True).distinct().order_by('city')
    areas = addpg.objects.filter(gender=gender, city=selected_city, approved=True).values_list('area', flat=True).distinct().order_by('area')
    
    return render(request, 'city.html', {
        'pg_list': pg_list,
        'cities': cities,
        'areas': areas,
        'gender': gender,
        'selected_city': selected_city,
        'selected_area': selected_area,
        'search_query': search_query,
        'selected_radius': selected_radius,
    })

#exmple
def pgarea(request, pg_id):
    pg = get_object_or_404(addpg, id=pg_id)
    return redirect('catpro', pgname=pg.pgname)

    # return render(request,'pgarea.html')


# owner register form

# owner register form
def register_owner(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('mob')
        password = request.POST.get('password')
        address = request.POST.get('add')
        personal_photo = request.FILES.get('personalphoto')
        securityquestion1 = request.POST.get('security_question1')
        securityanswer1 = request.POST.get('security_answer1')
        securityquestion2 = request.POST.get('security_question2')
        securityanswer2 = request.POST.get('security_answer2')

        owner = ownerregistration(
            name=name,
            email=email,
            phone_number=phone_number,
            password=password,
            address=address,
            personal_photo=personal_photo,
            securityquestion1=securityquestion1,
            securityanswer1=securityanswer1.lower(),  # store in lowercase for case-insensitive matching
            securityquestion2=securityquestion2,
            securityanswer2=securityanswer2.lower(),
            approved=False
        )

        owner.save()
        messages.success(request, 'Registration submitted successfully. Your account is pending approval.')
        return redirect('ownerlogin')
    else:
        return render(request, 'register_owner.html')

def approve_owner(request, owner_id):
    if not request.user.is_superuser:
        return redirect('home')  # Redirect if not an admin

    owner = get_object_or_404(ownerregistration, id=owner_id)
    if request.method == 'POST':
        owner.approved = True
        owner.save()
        messages.success(request, 'Owner registration approved.')
        return redirect('admin_dashboard')  # Redirect to admin dashboard

    return render(request, 'approve_owner.html', {'owner': owner})


def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')  # Redirect if not an admin

    pending_owners = ownerregistration.objects.filter(approved=False)
    return render(request, 'admin_dashboard.html', {'pending_owners': pending_owners})

#example
def loginsel(request):
    return render(request,'loginsel.html')

#owner page show addpg and add room
def owner(request):
    # Check if the owner is logged in
    if 'email' in request.session:
        # Retrieve the logged-in owner's information
        owner_email = request.session['email']
        try:
            owner = ownerregistration.objects.get(email=owner_email)
        except ownerregistration.DoesNotExist:
            owner = None
        return render(request, 'owner.html', {'owner': owner})
    else:
        return redirect('login')  # Redirect to login if not logged in
def admin_login(request):
    return render(request,'admin_login.html')


#owner login from
def owner_login(request):
    if request.method == 'POST':
        try:
            user = ownerregistration.objects.get(email=request.POST['email'])
            
            if user.approved:
                if user.password == request.POST['password']:
                    request.session['email'] = user.email
                    return redirect('owner')  # Redirect to the owner dashboard
                else:
                    return render(request, 'owner_login.html', {'pass': "Password is invalid"})
            else:
                return render(request, 'owner_login.html', {'notregstered': "Your account is pending approval."})
        
        except ownerregistration.DoesNotExist:
            return render(request, 'owner_login.html', {'notregstered': "You need to register first."})
    else:
        return render(request, 'owner_login.html')
    
# Owner Forgot Password View (email verification)
def owner_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            owner = ownerregistration.objects.get(email=email)
            request.session['reset_email'] = email
            return redirect('owner_security_questions')
        except ownerregistration.DoesNotExist:
            messages.error(request, "Email does not exist")
            return redirect('owner_forgot_password')
    return render(request, 'owner_forgot_password.html')

# Security Questions Verification View
def owner_security_questions(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('owner_forgot_password')
    
    owner = ownerregistration.objects.get(email=email)
    
    if request.method == 'POST':
        answer1 = request.POST.get('answer1', '').lower()
        answer2 = request.POST.get('answer2', '').lower()
        
        if (answer1 == owner.securityanswer1 and 
            answer2 == owner.securityanswer2):
            return redirect('owner_change_password')
        else:
            messages.error(request, "Incorrect answers to security questions")
    
    context = {
        'question1': owner.securityquestion1,
        'question2': owner.securityquestion2,
        'email': email
    }
    return render(request, 'owner_security_questions.html', context)

# Owner Change Password View
def owner_change_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('owner_forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords don't match")
            return redirect('owner_change_password')
        
        try:
            owner = ownerregistration.objects.get(email=email)
            owner.password = new_password
            owner.save()
            
            # Clear the session
            if 'reset_email' in request.session:
                del request.session['reset_email']
            
            messages.success(request, "Password changed successfully")
            return redirect('ownerlogin')
        except ownerregistration.DoesNotExist:
            messages.error(request, "An error occurred")
            return redirect('owner_change_password')
    
    return render(request, 'owner_change_password.html')    

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import ownerregistration, addpg, PGImage

def add_pg(request):
    if request.method == 'POST':
        # Ensure owner is logged in
        if 'email' in request.session:
            owner_email = request.session['email']
            try:
                owner = ownerregistration.objects.get(email=owner_email)
            except ObjectDoesNotExist:
                messages.error(request, 'Owner not found. Please log in again.')
                return redirect('login')

            # Fetch form data
            pgname = request.POST.get('pgname')
            pgimage = request.FILES.get('pgimage')
            pglogo = request.FILES.get('pglogo')
            pgvideo = request.FILES.get('pgvideo')
            gender = request.POST.get('gender')
            state = request.POST.get('pgstate')
            city = request.POST.get('city')
            area = request.POST.get('area')
            pgmanager = request.POST.get('pgmanager')
            address = request.POST.get('address')
            additional_images = request.FILES.getlist('pgimages')  # Get multiple images
            
            # Get selected amenities as a comma-separated string
            amenities = request.POST.getlist('amenities')
            amenities_str = ",".join(amenities) if amenities else ''

            # Save the PG request as unapproved
            pg = addpg(
                pgname=pgname,
                pgimage=pgimage,
                pglogo=pglogo,
                pgvideo=pgvideo,
                gender=gender,
                state=state,
                city=city,
                area=area,
                pgmanager=pgmanager,
                address=address,
                owner_email=owner.email,
                owner_password=owner.password,
                approved=False,
                amenities=amenities_str
            )
            pg.save()

            # Save additional images
            for image in additional_images:
                PGImage.objects.create(
                    pg=pg,
                    image=image,
                    owner_email=owner.email
                )

            messages.success(request, 'Your PG has been submitted for admin approval.')
            return redirect('owner')
        else:
            messages.error(request, 'Please log in to add your PG.')
            return redirect('login')
    else:
        return render(request, 'addpg.html')

        


@csrf_exempt
def like_pg(request, pg_id):
    if request.method == 'POST':
        pg = get_object_or_404(addpg, id=pg_id)

        # Check if email exists in session
        user_email = request.session.get('email')
        if not user_email:
            return JsonResponse({'message': 'User not logged in.'}, status=401)

        # Retrieve the user based on the email
        try:
            user = userregister.objects.get(email=user_email)
        except userregister.DoesNotExist:
            return JsonResponse({'message': 'User not found.'}, status=404)

        # Check if the user has already liked this PG
        if Like.objects.filter(user=user, pg=pg).exists():
            return JsonResponse({'message': 'You have already liked this PG.'}, status=400)

        # Create a new like and increment the like count
        Like.objects.create(user=user, pg=pg)
        pg.likes += 1
        pg.save()
        return JsonResponse({'likes': pg.likes, 'message': 'Liked successfully!'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def comment_pg(request, pg_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        pg = get_object_or_404(addpg, id=pg_id)
        
        if content:
            Comment.objects.create(pg=pg, content=content)
            return JsonResponse({'success': True, 'message': 'Comment added successfully!'})
        
        return JsonResponse({'success': False, 'message': 'Comment cannot be empty.'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def addroom(request):
    if request.method == 'POST':
        if 'email' in request.session:
            owner_email = request.session['email']
            owner = ownerregistration.objects.get(email=owner_email)
            pgname = request.POST.get('pgname')
            room_type = request.POST.get('room-type')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            price = request.POST.get('price')
            qty = request.POST.get('qty')
            room_ac = request.POST.get('room_ac')
            deposit = request.POST.get('deposit')  # New deposit field
            
            city = request.POST.get('city')
            area = request.POST.get('area')
            gender = request.POST.get('gender')

            # Calculate bad_qty based on room type and qty
            room_multipliers = {
                'single sharing': 1,
                'double sharing': 2,
                'three sharing': 3,
                'four sharing': 4,
                'five sharing': 5,
                'six sharing': 6,
                'seven sharing': 7,
                'eight sharing': 8,
            }
            bad_qty = room_multipliers.get(room_type, 0) * int(qty)

            # Save room data
            ro = room(
                pgname=pgname,
                name=room_type,
                description=description,
                image=image,
                price=price,
                qty=qty,
                bad_qty=bad_qty,
                city=city,
                area=area,
                gender=gender,
                owner_email=owner.email,
                owner_password=owner.password,
                ac_type=room_ac,
                deposit=deposit  # Save deposit field
            )

            ro.save()

            messages.success(request, 'Room added successfully.')
            return redirect('owner')
        else:
            return redirect('login')
    else:
        if 'email' in request.session:
            owner_email = request.session['email']
            pg_list = addpg.objects.filter(owner_email=owner_email)
            return render(request, 'addroom.html', {
                'pg_list': pg_list
            })
        else:
            return redirect('login')


def get_pg_details(request):
    pgname = request.GET.get('pgname')
    try:
        pg = addpg.objects.get(pgname=pgname)
        response_data = {
            'city': pg.city,
            'area': pg.area,
            'gender': pg.gender
        }
        return JsonResponse(response_data)
    except addpg.DoesNotExist:
        return JsonResponse({'error': 'PG not found'}, status=404)






def submit_feedback(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')  # Get feedback text from the form

        if feedback_text:
            # Ensure owner is logged in
            if 'email' in request.session:
                owner_email = request.session['email']
                try:
                    # Fetch the owner's details
                    owner = ownerregistration.objects.get(email=owner_email)
                    # Create a new feedback entry
                    Feedback.objects.create(
                        owner_email=owner.email,
                        owner_password=owner.password,
                        feedback_text=feedback_text
                    )
                    messages.success(request, 'Thank you for your feedback!')
                except ownerregistration.DoesNotExist:
                    messages.error(request, 'Owner not found. Please log in again.')
                    return redirect('login')
            else:
                messages.error(request, 'Please log in to submit feedback.')
                return redirect('login')
        else:
            messages.error(request, 'Feedback cannot be empty.')

    return redirect('owner')  # Redirect to the home page or any other page   

@login_required
def upload_pg_images(request):
    if request.method == 'POST':
        pg_id = request.POST.get('pg_name')
        pg_instance = addpg.objects.get(id=pg_id)
        
        if pg_instance.owner_email == request.user.email:
            pg_images = PGImage(pg_name=pg_instance, owner_email=request.user.email, owner_password=request.user.password)
            
            for i in range(1, 11):
                image_field = f'image{i}'
                if image_field in request.FILES:
                    setattr(pg_images, image_field, request.FILES[image_field])
            
            pg_images.save()
            return redirect('upload_success')
    
    # Show only PGs for the logged-in owner
    owner_pgs = addpg.objects.filter(owner_email=request.user.email)
    return render(request, 'allpgimage.html', {'pgs': owner_pgs})

def upload_success(request):
    return render(request, 'upload_success.html')
        
#user profile
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ownerregistration
from django.utils import timezone
from datetime import timedelta

def profile(request):
    if 'email' not in request.session:
        return redirect('login')

    try:
        owner = ownerregistration.objects.get(email=request.session['email'])
    except ownerregistration.DoesNotExist:
        messages.error(request, "Owner profile not found.")
        return redirect('login')

    if request.method == 'POST':
        # Update owner details
        owner.name = request.POST.get('name', owner.name)
        owner.phone_number = request.POST.get('phone', owner.phone_number)
        owner.address = request.POST.get('address', owner.address)
        
        # Handle profile photo upload
        if 'photo' in request.FILES:
            owner.personal_photo = request.FILES['photo']
        
        try:
            owner.save()
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')

        return redirect('profile')

    context = {
        'owner': owner,
        'session': True,
    }
    return render(request, 'profile.html', context)
    

#user profile update
def update(request):
    try:
        if request.method == 'POST':
            authordata = Author.object.get(name = 'd')
            authordata.name = request.POST['uname']
            authordata.email = request.POST['email']
            authordata.save()
            return render(request,'update.html',{'author':authordata})
        else: 
            authordata = Author.objects.get(name = 'd')   
            return render(request,'update.html',{'author':authordata})
    except Exception as e:
            return render(request,'update.html')    
    


def view_data(request):
    return render(request,"viewdata.html")

# View PG data - Show only the PGs owned by the logged-in owner
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# View PG data - Show only the PGs owned by the logged-in owner
def view_pg_data(request):
    if 'email' in request.session:
        owner_email = request.session['email']
        pgs = addpg.objects.filter(owner_email=owner_email, approved=True).prefetch_related('images')
        
        if request.method == 'POST':
            pg_id = request.POST.get('pg_id')
            pg = get_object_or_404(addpg, id=pg_id, owner_email=owner_email)

            if 'update_pg' in request.POST:
                pg.pgname = request.POST.get('pgname', pg.pgname)
                pg.gender = request.POST.get('gender', pg.gender)
                pg.state = request.POST.get('state', pg.state)
                pg.city = request.POST.get('city', pg.city)
                pg.area = request.POST.get('area', pg.area)
                pg.pgmanager = request.POST.get('pgmanager', pg.pgmanager) 
                
                if request.FILES.get('pglogo'):
                    pg.pglogo = request.FILES.get('pglogo')
                if request.FILES.get('pgimage'):
                    pg.pgimage = request.FILES.get('pgimage')
                if request.FILES.get('pgvideo'):
                    pg.pgvideo = request.FILES.get('pgvideo')
                
                pg.save()

                # Handle additional images
                additional_images = request.FILES.getlist('additional_images')
                for image in additional_images:
                    PGImage.objects.create(pg=pg, image=image, owner_email=owner_email)

                messages.success(request, 'PG updated successfully.')
                return redirect('view_pg_data')

            elif 'delete_pg' in request.POST:
                pg.delete()
                messages.success(request, 'PG deleted successfully.')
                return redirect('view_pg_data')

        return render(request, 'viewpgdata.html', {'pgs': pgs})
    return redirect('login')

def get_pg_images(request):
    if request.method == 'GET' and 'pg_id' in request.GET:
        pg_id = request.GET.get('pg_id')
        images = PGImage.objects.filter(pg_id=pg_id)
        
        image_data = [{
            'id': image.id,
            'image_url': image.image.url
        } for image in images]
        
        return JsonResponse({'images': image_data})
    return JsonResponse({'images': []})

@csrf_exempt
def delete_pg_image(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_id = data.get('image_id')
            pg_id = data.get('pg_id')
            
            # Verify the image belongs to the PG and the owner
            owner_email = request.session.get('email')
            if owner_email:
                image = get_object_or_404(PGImage, id=image_id, pg_id=pg_id, owner_email=owner_email)
                image.delete()
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import room, addpg  # Assuming addpg is the model for PG details

def view_room_data(request):
    if 'email' in request.session:
        owner_email = request.session['email']
        pgs = addpg.objects.filter(owner_email=owner_email)  # Fetch all PGs owned by the logged-in owner
        selected_pg = request.GET.get('pg')  # Get the selected PG from the query parameter

        # Filter rooms based on the selected PG
        if selected_pg:
            rooms = room.objects.filter(owner_email=owner_email, pgname=selected_pg)
        else:
            rooms = room.objects.filter(owner_email=owner_email)

        if request.method == 'POST':
            room_id = request.POST.get('room_id')
            ro = get_object_or_404(room, id=room_id, owner_email=owner_email)

            if 'update_room' in request.POST:
                ro.pgname = request.POST.get('pgname', ro.pgname)
                ro.name = request.POST.get('name', ro.name)  # Room type (name) entered manually
                ro.description = request.POST.get('description', ro.description)
                ro.price = request.POST.get('price', ro.price)
                ro.qty = int(request.POST.get('qty', ro.qty))
                ro.city = request.POST.get('city', ro.city)
                ro.area = request.POST.get('area', ro.area)

                if request.FILES.get('image'):
                    ro.image = request.FILES.get('image')

                # Calculate bad_qty based on the room type
                multiplier_map = {
                    'single sharing': 1,
                    'double sharing': 2,
                    'three sharing': 3,
                    'four sharing': 4,
                    'five sharing': 5,
                    'six sharing': 6,
                    'seven sharing': 7,
                    'eight sharing': 8
                }
                multiplier = multiplier_map.get(ro.name.lower(), 1)  # Default multiplier is 1
                ro.bad_qty = ro.qty * multiplier
                ro.save()
                messages.success(request, 'Room updated successfully.')
                return redirect('view_room_data')

            elif 'delete_room' in request.POST:
                ro.delete()
                messages.success(request, 'Room deleted successfully.')
                return redirect('view_room_data')

        return render(request, 'viewroomdata.html', {
            'rooms': rooms,
            'pgs': pgs,
            'selected_pg': selected_pg
        })
    else:
        return redirect('login')

def view_booking_data(request):
    owner_email = request.user.email  # Assuming the logged-in owner
    # Fetch all PGs owned by the logged-in owner
    owned_pgs = addpg.objects.filter(owner_email=owner_email)
    
    # Now fetch UserProfile data for the relevant PGs
    bookings = UserProfile.objects.filter(location__in=[pg.city for pg in owned_pgs])  # Assuming the location matches PG city

    return render(request, 'viewbookingdata.html', {'profiles': bookings})



    
#user checkout
def checkout(request, user_id):
    if 'email' not in request.session:
        return redirect('login')  # Redirect to login page if not logged in
    
    try:
        # Fetch the user profile
        user_profile = UserProfile.objects.get(id=user_id)
        
       
        room = room.objects.get(name=user_profile.room_type)
        
        # Increase the room quantity by 1
        room.qty += 1
        room.save()
        
       
        user_profile.delete()  

        
        
        return redirect('checkout_success')  # Redirect to a success page
    except room.DoesNotExist:
        return HttpResponse(f"Error: Room associated with the booking does not exist.")
    except UserProfile.DoesNotExist:
        return HttpResponse(f"Error: User profile does not exist.")
    except Exception as e:
        return HttpResponse(f"Error during checkout: {e}")


#user checkout
def checkout(request, user_id):
    if 'email' not in request.session:
        return redirect('login')  # Redirect to login page if not logged in
    
    try:
        # Fetch the user profile
        user_profile = UserProfile.objects.get(id=user_id)
        
       
        room = room.objects.get(name=user_profile.room_type)
        
        # Increase the room quantity by 1
        room.qty += 1
        room.save()
        
       
        user_profile.delete()  

        
        
        return redirect('checkout_success')  # Redirect to a success page
    except room.DoesNotExist:
        return HttpResponse(f"Error: Room associated with the booking does not exist.")
    except UserProfile.DoesNotExist:
        return HttpResponse(f"Error: User profile does not exist.")
    except Exception as e:
        return HttpResponse(f"Error during checkout: {e}")


# user book time payment



# user cancelled payment
def payment_cancelled(request):
    messages.error(request, "Payment was cancelled.")
    return redirect('index')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Check if the email exists in the userregister model
            user = userregister.objects.get(email=email)
            otp = random.randint(1000, 9999)  # Generate a 4-digit OTP
            request.session['otp'] = otp  # Store OTP in session
            request.session['email'] = email  # Store email in session
            # Send OTP via email
            send_mail(
                'Password Reset OTP',
                f'Your OTP is: {otp}',
                'allpghub@gmail.com',
                [email],
                fail_silently=False,
            )
            return redirect('otp_verify')  # Redirect to OTP verification page
        except userregister.DoesNotExist:
            messages.error(request, "Email does not exist")
            return redirect('forgot_password')
    return render(request, 'forgot_password.html')


def otp_verify(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        if entered_otp == str(stored_otp):
            return redirect('change_password')  # Redirect to change password page
        else:
            messages.error(request, "Invalid OTP")
            return redirect('otp_verify')
    return render(request, 'otp_verify.html')    

def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        email = request.session.get('email')  # Retrieve email from session
        try:
            # Retrieve the user using the stored email in the session
            user = userregister.objects.get(email=email)
            user.password = new_password
            user.save()  # Save the changes to the database
            messages.success(request, "Password changed successfully")
            return redirect('login')  # Redirect to login page after success
        except userregister.DoesNotExist:
            messages.error(request, "An error occurred")
            return redirect('change_password')
    return render(request, 'change_password.html')    



# Owner Forgot Password View

# Owner OTP Verify View
def owner_otp_verify(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        
        if entered_otp == str(stored_otp):
            return redirect('owner_change_password')  # Redirect to change password page
        else:
            messages.error(request, "Invalid OTP")
            return redirect('owner_otp_verify')
    
    return render(request, 'owner_otp_verify.html')

# Owner Change Password View



#ajay sir task
def pg_list_view(request):
    # fetch all PGs
    pg_list = addpg.objects.all()

    # get distinct cities for dropdown
    cities = addpg.objects.values_list('city', flat=True).distinct()
    
    # check if a city is selected from the dropdown
    selected_city = request.GET.get('city', None)
    if selected_city:
        pg_list = pg_list.filter(city=selected_city)

   
    areas = pg_list.values_list('area', flat=True).distinct()

    
    selected_area = request.GET.get('area', None)
    if selected_area:
        pg_list = pg_list.filter(area=selected_area)

    pg_details = []
    for pg in pg_list:
        # fetch rooms and pg details
        rooms = room.objects.filter(pgname=pg.pgname)  # use the pgname to fetch rooms

        available_rooms = [r for r in rooms if r.qty > 0]  
        booked_rooms = [r for r in rooms if r.qty == 0]  

        # prepare to count quantities of available rooms by name
        available_rooms_qty_by_name = {}
        for r in available_rooms:
            if r.name in available_rooms_qty_by_name:
                available_rooms_qty_by_name[r.name] += r.qty
            else:
                available_rooms_qty_by_name[r.name] = r.qty

        pg_details.append({
            'pg': pg,
            'rooms': rooms,
            'available_rooms_count': len(available_rooms),
            'available_rooms_qty': sum(r.qty for r in available_rooms),  # sum of quantities of available rooms
            'booked_rooms_count': len(booked_rooms),
            'available_rooms_qty_by_name': available_rooms_qty_by_name,  # add this line
        })

    return render(request, 'pg_list.html', {
        'pg_details': pg_details,
        'cities': cities,
        'selected_city': selected_city,
        'areas': areas, 
        'selected_area': selected_area,  
    })




#owner add weekly food in pg
def add_food(request):
    # Ensure the user is logged in
    if 'email' not in request.session:
        return redirect('login')  # Redirect to login if not logged in

    # Get the owner's email from the session
    owner_email = request.session['email']

    if request.method == 'POST':
        pg_id = request.POST.get('pg_id')
        pg = addpg.objects.filter(id=pg_id).first()
        if not pg or pg.owner_email != owner_email:
            return redirect('add_food')  # If PG not found or not owned by the user, redirect

        pg_name = pg.pgname  # Get the PG name

        # Initialize lists to hold entries for each meal type
        breakfast_entries = []
        lunch_entries = []
        dinner_entries = []

        # Add data for each day of the week
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            # Create entries for breakfast, lunch, and dinner with pg_id and pgname
            breakfast = Breakfast.objects.create(
                day=day,
                food_menu=request.POST.get(f'{day.lower()}_breakfast_menu'),
                drink=request.POST.get(f'{day.lower()}_breakfast_drink'),
                food_image=request.FILES.get(f'{day.lower()}_breakfast_image_menu'),
                drink_image=request.FILES.get(f'{day.lower()}_breakfast_image_drink'),
                pg_id=pg_id,
                pgname=pg_name
            )
            breakfast_entries.append(breakfast)

            lunch = Lunch.objects.create(
                day=day,
                food_menu=request.POST.get(f'{day.lower()}_lunch_menu'),
                drink=request.POST.get(f'{day.lower()}_lunch_drink'),
                food_image=request.FILES.get(f'{day.lower()}_lunch_image_menu'),
                drink_image=request.FILES.get(f'{day.lower()}_lunch_image_drink'),
                pg_id=pg_id,
                pgname=pg_name
            )
            lunch_entries.append(lunch)

            dinner = Dinner.objects.create(
                day=day,
                food_menu=request.POST.get(f'{day.lower()}_dinner_menu'),
                drink=request.POST.get(f'{day.lower()}_dinner_drink'),
                food_image=request.FILES.get(f'{day.lower()}_dinner_image_menu'),
                drink_image=request.FILES.get(f'{day.lower()}_dinner_image_drink'),
                pg_id=pg_id,
                pgname=pg_name
            )
            dinner_entries.append(dinner)

        # Weekly Meal Plan
        weekly_plan = WeeklyMealPlan.objects.create(pg_id=pg_id)

        # Set the entries for the weekly plan
        weekly_plan.breakfast.set(breakfast_entries)
        weekly_plan.lunch.set(lunch_entries)
        weekly_plan.dinner.set(dinner_entries)

        return redirect('owner')

    # Get the list of PGs registered by the current owner
    pg_list = addpg.objects.filter(owner_email=owner_email)

    # Days of the week
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    return render(request, 'addfood.html', {'days_of_week': days_of_week, 'pg_list': pg_list})


def success_page(request):
    return render(request, 'success_page.html')  # Create this template as well    

def add_food_view(request):
    if request.method == 'POST':
        # Handle form submission
        # Save data to the model here
        # After saving, redirect to the success page
        return redirect('success_page')  # Redirect to the success page
    return render(request, 'addfood.html')
    


def view_weekly_meal_plan(request, pg_id):
    # Try to find a WeeklyMealPlan for the given pg_id
    weekly_meal_plan = WeeklyMealPlan.objects.filter(pg_id=pg_id).first()

    # If no meal plan exists, redirect to a "No Data Found" page
    if not weekly_meal_plan:
        return redirect('no_data_found')

    # Pass the meal plan data to the template if found
    return render(request, 'view_weekly_meal_plan.html', {
        'weekly_meal_plan': weekly_meal_plan,
    })



def no_data_found(request):
    return render(request, 'no_data_found.html')




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Breakfast, Lunch, Dinner, addpg

def view_food_data(request):
    if 'email' in request.session:
        owner_email = request.session['email']
        pg_list = addpg.objects.filter(owner_email=owner_email)  # Get PGs for dropdown
        breakfast_entries = None
        lunch_entries = None
        dinner_entries = None
        pg_id = None

        if request.method == 'POST':
            pg_id = request.POST.get('pg_id')
            if pg_id:
                # Fetch food data for the selected PG
                breakfast_entries = Breakfast.objects.filter(pg_id=pg_id)
                lunch_entries = Lunch.objects.filter(pg_id=pg_id)
                dinner_entries = Dinner.objects.filter(pg_id=pg_id)

            action = request.POST.get('action')
            meal_type = request.POST.get('meal_type')
            meal_id = request.POST.get('meal_id')

            if action == 'update':
                # Get the correct model based on meal_type
                if meal_type == 'breakfast':
                    meal = get_object_or_404(Breakfast, id=meal_id)
                elif meal_type == 'lunch':
                    meal = get_object_or_404(Lunch, id=meal_id)
                elif meal_type == 'dinner':
                    meal = get_object_or_404(Dinner, id=meal_id)

                # Update food_menu and drink
                meal.food_menu = request.POST.get('food_menu')
                meal.drink = request.POST.get('drink')

                # Update food_image only if a new file is uploaded
                if request.FILES.get('food_image'):
                    meal.food_image = request.FILES['food_image']

                # Update drink_image only if a new file is uploaded
                if request.FILES.get('drink_image'):
                    meal.drink_image = request.FILES['drink_image']

                meal.save()
                return redirect('view_food_data')

            elif action == 'delete':
                if meal_type == 'breakfast':
                    meal = get_object_or_404(Breakfast, id=meal_id)
                elif meal_type == 'lunch':
                    meal = get_object_or_404(Lunch, id=meal_id)
                elif meal_type == 'dinner':
                    meal = get_object_or_404(Dinner, id=meal_id)

                meal.delete()
                return redirect('view_food_data')

            elif action == 'delete_all':
                # Delete all data for the selected PG
                Breakfast.objects.filter(pg_id=pg_id).delete()
                Lunch.objects.filter(pg_id=pg_id).delete()
                Dinner.objects.filter(pg_id=pg_id).delete()
                messages.success(request, 'All data for this PG has been deleted.')
                return redirect('view_food_data')

        context = {
            'pg_list': pg_list,
            'breakfast_entries': breakfast_entries,
            'lunch_entries': lunch_entries,
            'dinner_entries': dinner_entries,
            'pg_id': pg_id,
        }
        return render(request, 'viewfooddata.html', context)
    else:
        return redirect('login')  # Redirect if session expired