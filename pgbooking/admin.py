from django.shortcuts import render, get_object_or_404  # Add these imports at the top
from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib import admin
from .models import Blog,Author,userregister,image,category,Amenity,room,UserProfile,citytable,Feedback,ownerregistration,addpg,Breakfast, Lunch, Dinner, WeeklyMealPlan,Comment,RoomRating,Like,PGImage,Page,PagePhoto,VideoPage

# Register your models here.

admin.site.register(Blog)


class author_(admin.ModelAdmin):
    list_display = ['name','email']
    list_filter =['name','email']
    search_fields = ['name','email']

admin.site.register(Author,author_)


class user_(admin.ModelAdmin):
    list_display = ['name','email','add','mob','password','otp','datetime']

admin.site.register(userregister,user_)

admin.site.register(image)


class cat_(admin.ModelAdmin):
    list_display = ['id','name','image','multiplier']

admin.site.register(category,cat_)


class pro_(admin.ModelAdmin):
    list_display = ['id','pgname','name','description','image','price','deposit','qty','bad_qty','gender','city','area','ac_type','owner_email','owner_password','datetime']

admin.site.register(room,pro_)   

class UserProfileForm(admin.ModelAdmin):
    list_display = ['id','full_name', 'email', 'phone_number', 'location', 'gender', 'about', 'aadhaar_photo', 'personal_photo','room_type','datetime','pgname','room_price']
admin.site.register(UserProfile,UserProfileForm)                    

class citytablepro(admin.ModelAdmin):
     list_display = ['id','city_name','city_image','category']
admin.site.register(citytable,citytablepro)

class ownerregistrationpro(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'address', 'personal_photo', 'approved', 'approve_action','securityquestion1','securityanswer1','securityquestion2','securityanswer2')
    actions = ['approve_selected']

    def approve_action(self, obj):
        if not obj.approved:
            return mark_safe(f'<a href="{reverse("approve_owner", args=[obj.id])}">Approve</a>')
        return 'Approved'
    approve_action.short_description = 'Action'

    def approve_selected(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected registrations have been approved.")
    approve_selected.short_description = 'Approve selected registrations'

admin.site.register(ownerregistration, ownerregistrationpro)

class addpgpro(admin.ModelAdmin):
    list_display = ['id','pgname','pgimage','pglogo','gender','state','city','area','address','pgmanager','pgvideo','owner_email','owner_password','datetime','longitude','latitude','arealongitude','arealatitude','likes','approved','amenities']
admin.site.register(addpg,addpgpro)

class Amenitypro(admin.ModelAdmin):
    list_display = ['id','name','photo']

admin.site.register(Amenity,Amenitypro)

class compro(admin.ModelAdmin):
    list_display = ['pg','content','created_at']
admin.site.register(Comment,compro)    

class Likepro(admin.ModelAdmin):
    list_display = ['user','pg','created_at']
admin.site.register(Like,Likepro) 

class RoomRatingpro(admin.ModelAdmin):
    list_display = ['room','user','rating','comment','datetime']
admin.site.register(RoomRating,RoomRatingpro)    

class pgimagepro(admin.ModelAdmin):
    list_display = ['pg','image']
admin.site.register(PGImage,pgimagepro)

class DeleteUnapprovedRecordsJob(CronJobBase):
    RUN_EVERY_MINS = 60  # Run every hour

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'pgbooking.delete_unapproved_records'  # A unique code

    def do(self):
        now = timezone.now()
        unapproved_records = ownerregistration.objects.filter(approved=False, auto_delete_time__lte=now)
        unapproved_records.delete()




# Registering models for admin view
@admin.register(Breakfast)
class BreakfastAdmin(admin.ModelAdmin):
    list_display = ('day', 'food_menu', 'drink','food_image','drink_image','pg_id', 'pgname')

@admin.register(Lunch)
class LunchAdmin(admin.ModelAdmin):
    list_display = ('day', 'food_menu', 'drink','food_image','drink_image','pg_id', 'pgname')

@admin.register(Dinner)
class DinnerAdmin(admin.ModelAdmin):
    list_display = ('day', 'food_menu', 'drink','food_image','drink_image','pg_id', 'pgname')

class WeeklyMealPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'pg_id', 'get_pg_name')  # Valid fields/methods

admin.site.register(WeeklyMealPlan, WeeklyMealPlanAdmin)

def view_weekly_meal_plan(request, pg_id):
    weekly_meal_plan = get_object_or_404(WeeklyMealPlan, pg_id=pg_id)
    context = {
        'weekly_meal_plan': weekly_meal_plan,
    }
    return render(request, 'view_weekly_meal_plan.html', context)


class Feedbackpro(admin.ModelAdmin):
    list_display = ['owner_email','feedback_text','created_at']
admin.site.register(Feedback,Feedbackpro)    


# Register models
class Pagepro(admin.ModelAdmin):
    list_display = ['id','page_name']
admin.site.register(Page,Pagepro)

class PagePhotopro(admin.ModelAdmin):
    list_display = ['id','page','addname','photo','create_date']
admin.site.register(PagePhoto,PagePhotopro)


class VideoPagepro(admin.ModelAdmin):
    list_display = ['id','page','addname','video','created_date']
admin.site.register(VideoPage,VideoPagepro)