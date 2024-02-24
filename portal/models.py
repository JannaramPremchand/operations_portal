from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


CHOICES = (
        ('O', 'Operation'),
        ('C', 'Coordinator'),
        ('S', 'Student'),
    )

# Create your models here.
class Category(models.Model):
    CategoryId      = models.AutoField(primary_key=True)
    CategoryName    = models.CharField(max_length=250)

class Status(models.Model):
	StatusId = models.AutoField(primary_key=True)
	StatusName = models.CharField(max_length=30)

class Batch(models.Model):
	BatchId = models.AutoField(primary_key=True)
	BatchName = models.CharField(max_length=250, default = 'Name Me')
	CategoryId = models.ForeignKey(Category ,on_delete=models.CASCADE,db_column='CategoryId')
	BatchStartDate = models.DateField()
	BatchEndDate = models.DateField(blank=True , null=True)
	StatusId = models.ForeignKey(Status ,on_delete=models.CASCADE,db_column='StatusId')
	BatchEmail = models.CharField(max_length=250, default = 'BatchEmail')

class Session(models.Model):
	SessionId = models.AutoField(primary_key=True)
	BatchId = models.ForeignKey(Batch, on_delete=models.CASCADE,db_column='BatchId',null=True)
	SessionStartDate = models.DateTimeField()
	SessionEndDate = models.DateTimeField()
	sessioncoordinateuser = models.CharField(max_length=250,null=True)
	sessioninstructor =models.CharField(max_length=250,null=True)
	noofparticipants = models.IntegerField(default=1)
	sessiontitle = models.CharField(max_length=250,null=True,default='')
	sessionhash = models.CharField(max_length=250,null=True,default='')
	sessionfile = models.CharField(max_length=500,null=True)


class Student(models.Model):
	StudentId = models.AutoField(primary_key=True)
	StudentName = models.CharField(max_length=250)
	StudentContact = models.CharField(max_length=250,null=True)
	StudentEmail = models.CharField(max_length=250)
	StudentGender = models.CharField(max_length=250,null=True)


class StudentAttendance(models.Model):
	StudentAttendanceId = models.AutoField(primary_key=True)
	StudentId = models.ForeignKey(Student, on_delete=models.CASCADE,db_column='StudentId')
	SessionId = models.ForeignKey(Session, on_delete=models.CASCADE,db_column='SessionId')
	JoinTime = models.DateTimeField()
	LeaveTime = models.DateTimeField()
	Duration = models.CharField(max_length=20)

class Assignment(models.Model):
	AssignmentId = models.AutoField(primary_key=True)
	AssignmentTitle = models.CharField(max_length=250)
	AssignmentDescription = models.TextField()
	AssignmentLink = models.CharField(max_length=250)
	AssignmentAttachment = models.CharField(max_length=250)

class BatchAssignment(models.Model):
	BatchAssignmentId = models.AutoField(primary_key=True)
	BatchId = models.ForeignKey(Batch,on_delete=models.CASCADE,db_column='BatchId')
	AssignmentId = models.ForeignKey(Assignment,on_delete=models.CASCADE,db_column='AssignmentId')

class BatchOwner(models.Model):
	BatchId = models.ForeignKey(Batch,on_delete=models.CASCADE,db_column='BatchId')
	UserId = models.IntegerField()

class Course(models.Model):
	CourseId = models.AutoField(primary_key=True)
	CourseName = models.CharField(max_length = 250)

class CourseModule(models.Model):
	ModuleId = models.AutoField(primary_key=True)
	ModuleName = models.CharField(max_length=1000,default='Dummy Module')
	ModuleType = models.CharField(max_length = 250)
	LiveClasses = models.IntegerField(null=True)
	SelfLearning = models.IntegerField(null=True)
	SelfLearningLink = models.CharField(max_length=250,null=True)
	WorkLink = models.CharField(max_length=250,null=True)
	CourseId = models.ForeignKey(Course,on_delete=models.CASCADE,db_column='CourseId')
	ParentModuleId = models.ForeignKey("self", on_delete=models.CASCADE , db_column='ParentModuleId',null=True)

class CourseCategory(models.Model):
	CourseCategoryId = models.AutoField(primary_key=True)
	CategoryId = models.ForeignKey(Category,on_delete=models.CASCADE,db_column='CategoryId')
	CourseId = models.ForeignKey(Course,on_delete=models.CASCADE,db_column='CourseId')

class StudentWork(models.Model):
	WorkId = models.AutoField(primary_key=True)
	Name = models.CharField(max_length=250)
	Email = models.CharField(max_length=250)
	PercentFinish = models.CharField(max_length=250)
	AssignmentName = models.CharField(max_length=250)
	AssignmentProperty = models.CharField(max_length=250)
	AssignmentValue = models.CharField(max_length=250)

class BatchStudent(models.Model):
	BatchId = models.ForeignKey(Batch,on_delete=models.CASCADE,db_column='BatchId')
	StudentId = models.ForeignKey(Student,on_delete=models.CASCADE,db_column='StudentId')
	UserId      = models.ForeignKey(User, on_delete=models.CASCADE,db_column='UserId')
	StartDate = models.DateField()
	EndDate = models.DateField(blank=True , null=True)
	Status = models.TextField(max_length=30)

class StudentNotes(models.Model):
	NotesId = models.AutoField(primary_key=True)
	StudentId = models.ForeignKey(Student,on_delete=models.CASCADE,db_column='StudentId')
	NotesDate = models.DateTimeField(default=datetime.now, blank=True)
	NotesDescription = models.TextField()
	NotesEditor = models.CharField(max_length=250)

class assignment_data(models.Model):
	studentapidata = models.CharField(max_length=250,null=True)
	Name = models.CharField(max_length=250,null=True)
	Email = models.CharField(max_length=250,null=True)
	assignments =models.CharField(max_length=250,null=True)
	duedate = models.DateField(null=True)
	submiteddate = models.CharField(max_length=250,null=True)
	unsubmiteddate = models.CharField(max_length=250,null=True)
	returndate = models.CharField(max_length=250,null=True)
	reassingndate = models.CharField(max_length=250,null=True)
	status = models.CharField(max_length=250,null=True)
	feedback = models.CharField(max_length=300,null=True)
	points = models.CharField(max_length=5,null=True)
	assingment_delay = models.CharField(max_length=6,null=True)
	assingment_check_delay = models.CharField(max_length=6,null=True)
	batchid = models.ForeignKey(Batch,on_delete=models.CASCADE)
	studentid =models.ForeignKey(Student,on_delete=models.CASCADE)

class Teacher_class_detail(models.Model):
	Teacher_class_sequence = models.AutoField(primary_key=True)
	Teacher_name = models.CharField(max_length=250,null=True,)
	UserID = models.ForeignKey(User,on_delete=models.CASCADE,null=True,)
	Teacherintime = models.DateTimeField(null=True,)
	Teacherouttime =  models.DateTimeField(null=True,)
	Teacheremail = models.CharField(max_length=250,null=True,)
	teacher_duration = models.CharField(max_length=20,null=True,)

class ticketcategory(models.Model):
	ticketcategoryid =  models.AutoField(primary_key=True)
	ticketcategoryname = models.CharField(max_length=100,null=False)
	ticketcategorydesc = models.TextField()

class ticketsubcategory(models.Model):
	ticketsubcategoryid = models.AutoField(primary_key=True)
	ticketsubcategoryname = models.CharField(max_length=100,null=False)
	ticketsubcategorydesc = models.TextField()
	ticketcategoryid = models.ForeignKey(ticketcategory,on_delete=models.CASCADE,null=True,db_column='ticketcategoryid')

class ticketstatus(models.Model):
	ticketstatusid = models.AutoField(primary_key=True)
	ticketstatusname = models.CharField(max_length=100,null=False)

class tickets(models.Model):
	ticketid =  models.AutoField(primary_key=True)
	ticketdescription = models.TextField(null=False)
	ticketcreatedate = models.DateTimeField(default=datetime.now)
	lastmodifieddate = models.DateTimeField(default=datetime.now)
	ticketstatus = models.ForeignKey(ticketstatus,on_delete=models.CASCADE,db_column='ticketstatus',default=None)
	assignedtouser = models.ForeignKey(User,on_delete=models.CASCADE,db_column='assignedtouser',default=None)
	ticketcategory = models.ForeignKey(ticketcategory,on_delete=models.CASCADE,db_column='ticketcategory')
	ticketsubcategory = models.ForeignKey(ticketsubcategory,on_delete=models.CASCADE,db_column='ticketsubcategory')
	studentid = models.ForeignKey(Student,on_delete=models.CASCADE,db_column='studentid')
	stdname = models.CharField(max_length=100,db_column='stdname')
	stdemail = models.CharField(max_length=100,db_column='stdemail')

class mycelerytask(models.Model):
	mytaskId = models.AutoField(primary_key=True)
	access_token = models.CharField(max_length=5000,null=True)


class celerytask(models.Model):
	STATUS_CHOICES = (
        ('PEN', 'Pending'),
        ('COM', 'Complete'),
        ('ERR', 'Error'),
    )
	mytaskid = models.CharField(max_length=250)
	status = models.CharField(max_length=3, choices=STATUS_CHOICES, null=False, blank=False, default='PEN')


class meetingcategory(models.Model):
	meetingCategoryId  = models.AutoField(primary_key=True ,db_column='meetingCategoryId')
	categoryName =  models.CharField(max_length=250)



class Createmeetings(models.Model):
	meetingid = models.AutoField(primary_key=True)
	attendee = models.ForeignKey(User, on_delete=models.CASCADE,db_column='attendee')
	startdatetime = models.DateTimeField(default=datetime.now,db_column='startdatetime')
	enddatetime = models.DateTimeField(default=datetime.now,db_column='enddatetime')
	donotrepeat = models.ForeignKey(meetingcategory ,on_delete=models.CASCADE,db_column='donotrepeat')
	addchannels =   models.ForeignKey(Category ,on_delete=models.CASCADE,db_column='addchannels')
	locations = models.CharField(max_length=100,db_column='locations')
	meetingdetail = models.CharField(max_length=100,db_column='meetingdetail')


# class attendence_data(models.Model):
# 	attendenceid = models.AutoField(primary_key=True)
# 	Name = models.CharField(max_length=250,null=True)
# 	Email = models.CharField(max_length=250,null=True)
# 	attendenceinseconds =models.CharField(max_length=250,null=True)
# 	jointime = models.DateTimeField(default=datetime.now,db_column='jointime')
# 	leavetime = models.DateTimeField(default=datetime.now,db_column='leavetime')

class batchmeeting(models.Model):
	id = models.AutoField(primary_key=True)
	Batchid =models.IntegerField()
	# Batchemail =models.CharField(max_length=100,db_column='batchemail',null=True)