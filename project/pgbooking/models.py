from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
# Create your models here.

# example
class Blog(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.TextField()

    # def __str__(self):
    #     return self.name

#example
class Author(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return self.email

# userregister 
class userregister(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    add = models.TextField()
    password = models.CharField(max_length=200)
    mob = models.CharField(max_length=10)
    otp = models.CharField(max_length=6, null=True, blank=True)  # Add this line
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name        

# image (example)
class image(models.Model):
    image = models.ImageField(upload_to='catimg')

         # def __str__(self):
    #     return self.name

# category male and female
class category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='cat_img')
    multiplier = models.IntegerField(default=1)  # Add this field

    def __str__(self):
        return self.name


# user book the room and owner add the room
class room(models.Model):
    pgname = models.CharField(max_length=150)
    name = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='room_images/')
    price = models.CharField(max_length=10)
    qty = models.PositiveIntegerField()
    bad_qty = models.IntegerField(default=0)
    gender = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    ac_type = models.CharField(max_length=10, choices=[('AC', 'AC'), ('Non-AC', 'Non-AC')], default='Non-AC')
    owner_email = models.EmailField(null=True)
    owner_password = models.CharField(max_length=200, null=True)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New deposit field
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class RoomRating(models.Model):
    room = models.ForeignKey('room', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(userregister, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField(null=True, blank=True)
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.room.name} - {self.rating}"     

# user book the pg 
class UserProfile(models.Model):
    
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # Ensure email is unique
    phone_number = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    about = models.TextField(blank=True)  # Allow blank for optional info
    aadhaar_photo = models.ImageField(upload_to='aadhaar_photos/')  # Specify upload_to
    personal_photo = models.ImageField(upload_to='personal_photos/')  # Specify upload_to
    created_at = models.DateTimeField(auto_now_add=True)
    room_type = models.CharField(max_length=200, default=" ")
    datetime = models.DateTimeField(default=timezone.now)
    room_price = models.IntegerField(default=0)  # New field to store the total room price
    pgname = models.CharField(max_length=150)  # New field to store PG name
    
    def __str__(self):
        return self.full_name



# user add the addpg than not add this city than add but not add
class citytable(models.Model):
    city_name = models.CharField(max_length=50,unique=True)
    city_image = models.ImageField()
    category = models.ForeignKey(category,on_delete=models.CASCADE)

    def __str__(self):
        return self.city_name        

# ownerregistration
class ownerregistration(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=10, blank=True)
    password  = models.CharField(max_length=200)
    address = models.TextField()
    personal_photo = models.ImageField()
    datetime = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    auto_delete_time = models.DateTimeField(default=timezone.now() + timedelta(hours=72))  # 72 hours from creation

    #auto_delete_time = models.DateTimeField(default=lambda: timezone.now() + timedelta(hours=72))
 
    def __str__(self):
        return self.name

class Feedback(models.Model):
    owner_email = models.EmailField()  # Store the owner's email
    owner_password = models.CharField(max_length=200)  # Store the owner's password
    feedback_text = models.TextField()  # Field to store the feedback text
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the feedback was submitted

    def __str__(self):
        return f"Feedback by {self.owner_email} on {self.created_at}"        

# owner addpg
class addpg(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit primary key
    pgname = models.CharField(max_length=100)
    pgimage = models.ImageField(upload_to='images/')
    pgvideo = models.FileField(upload_to='videos/', null=True, blank=True)
    pglogo = models.ImageField(upload_to='logos/', null=True, blank=True)
    gender = models.CharField(max_length=20)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)  # New address field
    pgmanager = models.CharField(max_length=10, blank=True)
    owner_email = models.EmailField(null=True)
    owner_password = models.CharField(max_length=200, null=True)
    datetime = models.DateTimeField(default=timezone.now)
    likes = models.IntegerField(default=0)
    longitude = models.DecimalField(max_digits=18, decimal_places=14, null=True, blank=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=14, null=True, blank=True)
    arealongitude = models.DecimalField(max_digits=18, decimal_places=14, null=True, blank=True)
    arealatitude = models.DecimalField(max_digits=18, decimal_places=14, null=True, blank=True)
    approved = models.BooleanField(default=False)  # New field for approval status
    amenities = models.TextField(blank=True, null=True)  # Store amenities as a comma-separated string


    def __str__(self):
        return self.pgname

    class Meta:
        db_table = 'addpg'  # Retain existing table name


class Amenity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)  # Ensure amenity names are unique
    photo = models.ImageField(upload_to='amenities/', null=True, blank=True)  # Optional photo

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'amenities'  # Table name

class Comment(models.Model):
    pg = models.ForeignKey(addpg, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(userregister, on_delete=models.CASCADE)
    pg = models.ForeignKey(addpg, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pg')  # Ensure unique likes per user per PG    

class PGImage(models.Model):
    pg = models.ForeignKey('addpg', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    owner_email = models.EmailField() 
    
    def __str__(self):
        return f"Image for {self.pg.pgname}"


class Breakfast(models.Model):
    day = models.CharField(max_length=10)
    food_menu = models.CharField(max_length=255)
    drink = models.CharField(max_length=255)
    food_image = models.ImageField(upload_to='images/')
    drink_image = models.ImageField(upload_to='images/')
    pg_id = models.CharField(max_length=255, default='default_pg_id')  # Set a sensible default
    pgname = models.CharField(max_length=255, default='default_pg_name')  # Set a sensible default

    def __str__(self):
        return f"{self.day} - {self.food_menu} - {self.pgname}"

class Lunch(models.Model):
    day = models.CharField(max_length=10)
    food_menu = models.CharField(max_length=255)
    drink = models.CharField(max_length=255)
    food_image = models.ImageField(upload_to='images/')
    drink_image = models.ImageField(upload_to='images/')
    pg_id = models.CharField(max_length=255)  # Store PG ID
    pgname = models.CharField(max_length=255)  # Store PG Name

    def __str__(self):
        return f"{self.day} - {self.food_menu} - {self.pgname}"

class Dinner(models.Model):
    day = models.CharField(max_length=10)
    food_menu = models.CharField(max_length=255)
    drink = models.CharField(max_length=255)
    food_image = models.ImageField(upload_to='images/')
    drink_image = models.ImageField(upload_to='images/')
    pg_id = models.CharField(max_length=255)  # Store PG ID
    pgname = models.CharField(max_length=255)  # Store PG Name

    def __str__(self):
        return f"{self.day} - {self.food_menu} - {self.pgname}"

class WeeklyMealPlan(models.Model):
    pg_id = models.CharField(max_length=255)  # PG ID to be selected
    breakfast = models.ManyToManyField(Breakfast)
    lunch = models.ManyToManyField(Lunch)
    dinner = models.ManyToManyField(Dinner)

    def get_pg_name(self):
        # Assuming you have a model `addpg` with fields `id` and `pgname`
        pg_instance = addpg.objects.filter(id=self.pg_id).first()
        return pg_instance.pgname if pg_instance else "Unknown"

    def __str__(self):
        return f"PG: {self.pg_id}"
        

# Page model
class Page(models.Model):
    page_name = models.CharField(max_length=255)  # Name of the page

    def __str__(self):
        return self.page_name

# PagePhoto model
class PagePhoto(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)  # Foreign key to Page
    addname = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='photos/')  # Photo file (stored in 'photos/' directory)
    create_date = models.DateTimeField(auto_now_add=True)  # Automatically set the creation date

    def __str__(self):
        return f"Photo for {self.page.page_name}"

# VideoPage model
class VideoPage(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)  # Foreign key to Page
    addname = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/')  # Video file (stored in 'videos/' directory)
    created_date = models.DateTimeField(auto_now_add=True)  # Automatically set the creation date

    def __str__(self):
        return f"Video for {self.page.page_name}"        