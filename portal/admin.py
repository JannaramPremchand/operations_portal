from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Category)
admin.site.register(Status)
admin.site.register(Batch)
admin.site.register(Session)
admin.site.register(Student)
admin.site.register(StudentAttendance)
admin.site.register(Assignment)
admin.site.register(BatchAssignment)
admin.site.register(BatchOwner)
admin.site.register(Course)
admin.site.register(CourseModule)
admin.site.register(CourseCategory)
admin.site.register(StudentWork)
admin.site.register(BatchStudent)
admin.site.register(Teacher_class_detail)
admin.site.register(ticketcategory)
admin.site.register(ticketsubcategory)
admin.site.register(ticketstatus)
admin.site.register(tickets)
admin.site.register(batchmeeting)
admin.site.register(mycelerytask)