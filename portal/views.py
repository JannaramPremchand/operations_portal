from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login 
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from .raw_queries import *
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.models import Group
import json
from django.http import JsonResponse
#from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
# from django.template import RequestContext
from django.db import connection
import datetime
from django.conf import settings
import os
from django.core.files.storage import default_storage
from .Import_attendance_data import *
from .Import_grades import *
from django.contrib.auth.models import User
from django.contrib.auth.models import  Group
import pandas as pd
import math

from rest_framework.response import Response
from rest_framework.decorators import api_view
from portal.serializers import CreatemeetingsSerializer
# -----------------------------

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, timedelta
from dateutil import tz, parser
from portal.auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_token
from portal.graph_helper import *
from portal.graph_helper import create_event
from celery import shared_task
import time
from portal import task
import pandas as pd
from .serializers import *
# Create your views here.
cursor = connection.cursor()

def dictfetchall(cursor): 
    print("cursor",cursor)

    "Returns all rows from a cursor as a dict" 
    x = cursor.description
    return [
            dict(zip([col[0] for col in x], row)) 
            for row in cursor.fetchall() 
    ]

def home(request):
    if request.user.is_authenticated:
        sales_perm = User.objects.filter(pk=request.user.id, groups__name='Student').exists()
        if sales_perm==True:  
            print(sales_perm)
            programs =  Category.objects.all()
            #print('a',a.columns)
            return redirect('/mydashboard')
        else:
            return render(request,'index.html')
    else:
        return redirect('/login')


def login_req(request):
    # if request.user.is_authenticated:
    #     return redirect('/')
    # else:
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        print(username,password,"wwewew",user)
        if user is not None:
            login(request,user)
            #messages.info(request, f"You are now logged in as {username}.")
            return redirect("/")
        else:
            messages.error(request,"Invalid username or password..!!")
    
    # form = Usersignupform()
    return render(request,'login.html')



def batches(request):
    if request.user.is_authenticated :
        batch_info = Batch.objects.all()
        category = Category.objects.all()
        #student_info = BatchStudent.objects.raw(Total_Student_Count) 
        cursor.execute(Total_Student_Count)  
        student_info =  dictfetchall(cursor)  
        b_info = {"info" : batch_info , "s_info" : student_info, "category" : category}
        print("b_info******************^^^^^^^^^^^^^^^")
        print(b_info)
        if request.method == "POST":
            attendanceFile = request.FILES['attendanceFile']
            print(attendanceFile.name)

            file_name = default_storage.save('./static/attendance/'+attendanceFile.name, attendanceFile)

            messages.info(request,"File Saved Successfully! Please Wait until the attendance upload..")

            upload_attendance_files(filewithpath='./static/attendance/'+attendanceFile.name)

            messages.info(request,"Attendance Uploaded Successfully!!!")

            os.remove(os.path.join('./static/attendance/'+attendanceFile.name))


        return render(request,'batches.html', b_info)

    else:
        return redirect('/login')
    

# API Calls
def batches_api(request):
    if request.user.is_authenticated:
        batch_info = Batch.objects.all().values()  # convert QuerySet to a dictionary
        category = Category.objects.all().values()  # convert QuerySet to a dictionary
        cursor.execute(Total_Student_Count)
        student_info = dictfetchall(cursor)
        b_info = {"info": list(batch_info), "s_info": student_info, "category": list(category)}
        return JsonResponse({"data": b_info})
    else:
        return JsonResponse({"error": "User is not authenticated"}, status=401)
def batch_details_api(request, pk):
    if request.method != 'GET':
        return JsonResponse({"error": "Only GET method is supported for this endpoint"}, status=405)

    if request.user.is_authenticated:
        batch = Batch.objects.filter(BatchId=pk).values().first()  # Get first batch that matches the id and convert to dictionary
        if not batch:
            return JsonResponse({"error": "Batch not found"}, status=404)

        my_group = Group.objects.get(name='Student')
        upload_student_attendance(request, pk)

        # Assuming cursor is defined somewhere before
        cursor.execute(StudentAttendanceSummaryQuery.format(pk=pk))
        resultset = dictfetchall(cursor)
        student_attendance = {"sessions": resultset, "batch": batch}
        
        return JsonResponse(student_attendance)
    else:
        return JsonResponse({"error": "User is not authenticated"}, status=401)
def student_attendance_details_api(request, pk):
    if request.user.is_authenticated and request.user.groups.filter(name='Operation').exists():
        student_notes = StudentNotes.objects.filter(StudentId=pk).values()  # Get student notes
        cursor.execute(StudentAttendanceDetailsQuery.format(pk))
        resultset = dictfetchall(cursor)
        student_details = BatchStudent.objects.filter(StudentId=pk).values()  # Get student details
        student_details1 = Student.objects.filter(StudentId=pk).values()
        data = {"student_details1":list(student_details1),"studentDetails": list(student_details),"studentNotes": list(student_notes), "studentAttendanceDetails": resultset,}
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "User is not authenticated"}, status=401)



def batch_details(request,pk, methods=['GET' , 'POST']):
    print("************************************batch_details")
    if request.user.is_authenticated :
        Batch_i = Batch.objects.filter(BatchId=pk)
        my_group = Group.objects.get(name='Student')
        print("reqst",request)
        print("pk",pk)
        upload_student_attendance(request,pk)

        cursor.execute(StudentAttendanceSummaryQuery.format(pk=pk))
        resultset =  dictfetchall(cursor)
        studentattend = {"sess":resultset , "batch" : Batch_i}
        print(studentattend)
        
        return render(request,'batch_details.html' , studentattend)

    else:
        return redirect('/login')

# here
def fn_add_student(request,batch_id,stu_f_name,stu_l_name,stu_email,stu_password,stu_sta_date,stu_status):
    if request.user.is_authenticated :
        print("Batch ID:", batch_id)
        print("First Name:", stu_f_name)
        print("Last Name:", stu_l_name)
        print("Email:", stu_email)
        print("Password:", stu_password)
        print("Start Date:", stu_sta_date)
        print("Status:", stu_status)
        my_group = Group.objects.get(name='Student')
        print('mygroup',my_group)
        # Check if stu_l_name is NaN or None
        if isinstance(stu_l_name, float) and math.isnan(stu_l_name):
            stu_l_name = None  # If it's NaN, set it to None to avoid issues

        # Construct the user's full name
        if stu_f_name and not stu_l_name:
            # If last name is missing, use only the first name
            stu_name = stu_f_name
        elif not stu_f_name and stu_l_name:
            # If first name is missing, use only the last name
            stu_name = stu_l_name
        elif stu_f_name and stu_l_name:
            # If both first name and last name are present, concatenate them
            stu_name = f"{stu_f_name} {stu_l_name}"
        else:
            # Both first name and last name are missing
            stu_name = None

        # Ensure last_name is not None before creating the user
        if stu_l_name is None:
            stu_l_name = ''  # or provide a default value
        print("fn_add_student")
        print(stu_name)
        student = Student(
            StudentName = stu_name,
            StudentEmail = stu_email
            )
        student.save()

        user = User.objects.create_user(username=stu_email,
                             first_name=stu_f_name,
                             last_name=stu_l_name,
                             email=stu_email,
                             password=stu_password)
        stu_id  = Student.objects.latest('StudentId')
        us_id = User.objects.latest('id')
        my_group.user_set.add(us_id)
        batch_student = BatchStudent(
            StartDate = stu_sta_date,
            Status = stu_status,
            BatchId = Batch.objects.only('BatchId').get(BatchId=batch_id),
            StudentId = stu_id,
            UserId = us_id
            )
        batch_student.save()
        messages.info(request,"Student is Added......!!!!")


# This function returns batch category of a particular batch
def check_batch_category(batchId):
    print('check_batch_category')
    cursor.execute("""select CategoryName from portal_category join portal_batch on portal_category.CategoryId = portal_batch.CategoryId
                    where portal_batch.batchid = {}""".format(batchId))
    return cursor.fetchall()[0]

def upload_student_attendance(request,batchId):
    print("************************************upload_student_attendance")
    if request.method == "POST":

        if 'attendanceFile' in request.FILES :
            print("************************************upload_student_attendance_attendanceFile")
            attendanceFile = request.FILES['attendanceFile']

            file_name = default_storage.save('./static/attendance/'+attendanceFile.name, attendanceFile)

            messages.info(request,"File Saved Successfully! Please Wait until the attendance upload..")

            upload_attendance_files(batchId=batchId,filewithpath='./static/attendance/'+attendanceFile.name)

            messages.info(request,"Attendance Uploaded Successfully!!!")

            os.remove(os.path.join('./static/attendance/'+attendanceFile.name))
        else:
            print("************************************upload_student_attendance_attendanceFile_else")
            import_file = request.FILES['import_file']

            file_name = default_storage.save('./static/importStudents/'+import_file.name, import_file)

            df = pd.read_csv('./static/importStudents/'+import_file.name)

            if 'Temporary' in check_batch_category(batchId):
                print("****************************Temporary")
                email_csv = []
                for i in df.index:
                    print('Email' , df['email'][i])
                    if User.objects.filter(email=df['email'][i]).exists() :
                        email_csv.append(df['email'][i])
                txt = ''
                for email in email_csv :
                    txt = txt + "'" + email +"',"
                txt = txt[0:len(txt) -1]
                cursor.execute("""insert into portal_batchstudent (StartDate , EndDate , status, batchid, studentid, userid)
                                    select
                                    distinct
                                    (select BatchStartDate from portal_batch where batchid = {batchid}),
                                    null,
                                    'Active',
                                    {batchid},
                                    portal_student.StudentId,
                                    portal_batchstudent.userid
                                    from portal_student join portal_batchstudent on portal_student.StudentId = portal_batchstudent.StudentId
                                    where portal_student.StudentEmail in ({emailid})""".format(batchid=batchId,emailid=txt))
                conn.commit()

            else:
                print("************************************ else part")
                print(df)
                for i in df.index:
                    if pd.isna(df['password'][i]):
                        password = ''  # or set to some default value
                    else:
                        password = str(df['password'][i])
                    # Convert date format
                    if pd.isna(df['start_date'][i]):
                        start_date = None  # or set to some default value
                    else:
                        start_date = pd.to_datetime(df['start_date'][i], format='%d-%m-%Y').strftime('%Y-%m-%d')
                    print('df 176' , df['email'][i])
                    if User.objects.filter(email=df['email'][i]).exists() :
                        print('email',df['email'][i])
                        pass
                    else:
                        print(180)
                        fn_add_student(request,batch_id=batchId,stu_f_name=df['first_name'][i],stu_l_name=df['last_name'][i],stu_email=df['email'][i],stu_password=password,stu_sta_date=start_date,stu_status=df['status'][i])

            messages.info(request,"Students are imported......!!!!")

            os.remove(os.path.join('./static/importStudents/'+import_file.name))    


#see all users
@csrf_protect
def fetchitems(request):
    print('request.GET', request.GET)
    if request.method=="POST":
        id = request.POST['option']
        batch_k = request.POST['batch_k']
        print('batch_k',id)
        if id=='Top 10 Students':
            cursor.execute(StudentAttendanceSummaryQueryTop10.format(pk=batch_k))
            results = cursor.fetchall()
            x = cursor.description
            #print('all_product',Session.objects.raw(StudentHighestPlacement))
            resultsList = []   
            for r in results:
                i = 0
                d = {}
                while i < len(x):
                    d[x[i][0]] = r[i]
                    i = i+1
                resultsList.append(d)
            print('all_product',resultsList)
            
            return JsonResponse(resultsList, safe=False)

        elif id=='Students with Highest Placement Chance':
            cursor.execute(StudentHighestPlacement.format(pk=batch_k))
            results = cursor.fetchall()
            x = cursor.description
            #print('all_product',Session.objects.raw(StudentHighestPlacement))
            resultsList = []   
            for r in results:
                i = 0
                d = {}
                while i < len(x):
                    d[x[i][0]] = r[i]
                    i = i+1
                resultsList.append(d)
            print('all_product',resultsList)
            
            return JsonResponse(resultsList, safe=False)

        elif id=='Students with Lowest Placement Chance':
            cursor.execute(StudentLowestPlacement.format(pk=batch_k))
            results = cursor.fetchall()
            x = cursor.description
            #print('all_product',Session.objects.raw(StudentHighestPlacement))
            resultsList = []   
            for r in results:
                i = 0
                d = {}
                while i < len(x):
                    d[x[i][0]] = r[i]
                    i = i+1
                resultsList.append(d)
            print('all_product',resultsList)
            
            return JsonResponse(resultsList, safe=False)

        else:
            cursor.execute(StudentAttendanceSummaryQuery.format(pk=batch_k))
            results = cursor.fetchall()
            x = cursor.description
            #print('all_product',Session.objects.raw(StudentHighestPlacement))
            resultsList = []   
            for r in results:
                i = 0
                d = {}
                while i < len(x):
                    d[x[i][0]] = r[i]
                    i = i+1
                resultsList.append(d)
            print('all_product',resultsList)
            
            return JsonResponse(resultsList, safe=False)

#Batch Fiter by Category
@csrf_protect
def batchfilter(request):
    if request.method=="POST":

        categoryFilter = request.POST['option']

        print('batch_k',categoryFilter)

        if categoryFilter == 'Category Filtering':
            cursor.execute(Total_Student_Count)
            results = cursor.fetchall()
            x = cursor.description
            #print('all_product',Session.objects.raw(StudentHighestPlacement))
            resultsList = []   
            for r in results:
                i = 0
                d = {}
                while i < len(x):
                    d[x[i][0]] = r[i]
                    i = i+1
                resultsList.append(d)
            print('all_product',resultsList)
            
            return JsonResponse(resultsList, safe=False)
        else:

            cursor.execute(BatchFiterByCategory.format(category=categoryFilter))
            results = cursor.fetchall()
            x = cursor.description
            #print('all_product',Session.objects.raw(StudentHighestPlacement))
            resultsList = []   
            for r in results:
                i = 0
                d = {}
                while i < len(x):
                    d[x[i][0]] = r[i]
                    i = i+1
                resultsList.append(d)
            print('all_product',resultsList)
            
            return JsonResponse(resultsList, safe=False)


# Student Dashboard Overview 
def convert(list):
    return tuple(list)

# Student Dashboard Overview 
# @csrf_protect
def mydashboard(request , methods=['GET' , 'POST']):
    if request.user.is_authenticated and  User.objects.filter(groups__name='Student').exists() :
        
        Stu_Details = BatchStudent.objects.filter(UserId=request.user.id)
        s_detail = {"Stu_Details" : Stu_Details}
        batch_list = [0]
        for i in s_detail['Stu_Details']:
            print('Name ', i.BatchId.BatchId , i.StudentId.StudentId)
            batchId = i.BatchId.BatchId
            studentId = i.StudentId.StudentId
            batch_list.append(batchId)
        print('l',batch_list)
        batch_tuple = convert(batch_list)
        print('t',batch_tuple)
        print('b',batchId)
        cursor.execute(StudentAttendanceSummaryQueryTop1.format(pk=batch_tuple,sId=studentId))
        resultset =  dictfetchall(cursor)
        print(resultset)
        Stu_Details = BatchStudent.objects.filter(UserId=request.user.id)
        return render(request,'student-dashboard.html',{'st_att_sum' :resultset , 'Stu_Details' : Stu_Details})
    else:
        return redirect('/login')


def studentassignmentdetails(request,pk):
    if request.user.is_authenticated and  User.objects.filter(groups__name='Operation').exists() :
        studentNotes = StudentNotes.objects.filter(StudentId=pk)
        cursor.execute(StudentAttendanceDetailsQuery.format(pk))
        resultset =  dictfetchall(cursor)
        StudentDetails = BatchStudent.objects.filter(StudentId=pk)
        resultset =  dictfetchall(cursor)

        Assignment_data1 = assignment_data.objects.all().values()
        print(Assignment_data1)
        Assignment_data = assignment_data.objects.filter(studentid=pk)
        print('no data')
        s = {"studentNotes" : studentNotes,"st_att_sum" :resultset , "stu_det" : StudentDetails,"Assignment_data":Assignment_data}

        return render(request,'student-assignment-details.html',s)
    else:
        return redirect('/login')

def studentattendancedetails(request,pk):
    if request.user.is_authenticated and User.objects.filter(groups__name='Operation').exists() :
        studentNotes = StudentNotes.objects.filter(StudentId=pk)
        cursor.execute(StudentAttendanceDetailsQuery.format(pk))
        resultset =  dictfetchall(cursor)
        print("resultset")
        print(resultset)
        StudentDetails = BatchStudent.objects.filter(StudentId=pk)
        s = {"studentNotes" : studentNotes,"st_att_sum" :resultset , "stu_det" : StudentDetails}
        print("*****************^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(s)
        return render(request,'student-attendance-details.html',s)

    else:
        return redirect('/login')

def myAttendanceDetails(request,pk):
    if request.user.is_authenticated and  User.objects.filter(groups__name='Student').exists() :
        print('my')
        cursor.execute(StudentAttendanceDetailsQuery.format(pk))
        resultset =  dictfetchall(cursor)
        #StudentAttendanceSummary =  StudentAttendance.objects.filter(StudentId=pk,JoinTime__isnull=False,LeaveTime__isnull=False)
        StudentDetails = BatchStudent.objects.filter(StudentId=pk)
        s = {"st_att_sum" :resultset , "stu_det" : StudentDetails}
        print("My")
        return render(request,'my-attendance-details.html',s)
    else:
        return redirect('/login')

def myprofile(request):
    if request.user.is_authenticated :
        batch_info = BatchStudent.objects.filter(UserId=request.user.id)
        b_info = {"info" : batch_info}
        if request.method == "POST":
            student_Contact = request.POST['student_contact']
            student_id = request.POST['student_id']
            student = Student.objects.filter(StudentId=student_id)
            student.update(StudentContact=student_Contact)
            return redirect('/mydashboard')

        return render(request,'student-profile.html', b_info)

    else:
        return redirect('/login')


def logout(request):
    #logout(request)
    messages.info(request,"Logout Successfully")
    return redirect("/login")

def allcourses(request):
    if request.user.is_authenticated :
        courses =  CourseCategory.objects.raw(AllCoursesQuery)
        #print('a',a.columns)
        return render(request,'all-courses.html' ,{'all_courses':courses})

    else:
        return redirect('/login')

def allmodules(request,pk):
    if request.user.is_authenticated :
        modules =  CourseModule.objects.raw(AllModulesQuery.format(pk))
        #print('a',a.columns)
        return render(request,'all-modules.html' ,{'all_modules':modules})

    else:
        return redirect('/login')

def allprograms(request):
    if request.user.is_authenticated :
        programs =  Category.objects.all()
        #print('a',a.columns)
        return render(request,'all-programs.html' ,{'all_programs':programs})

    else:
        return redirect('/login')

def myperformance(request):
    if request.user.is_authenticated :
        sales_perm = User.objects.filter(pk=request.user.id, groups__name='Student').exists()
        if sales_perm==True:  
            print(sales_perm)
            programs =  Category.objects.all()
            #print('a',a.columns)
            return render(request,'student-grades.html' ,{'all_programs':programs,'sales_perm':sales_perm})
        else:
            return redirect('/login')
    else:
        return redirect('/login')

def assignments(request,pk):
    if request.user.is_authenticated :
        if request.method == "POST":
            grades = request.POST['radio1']
            print('grades',grades)
            if grades == 'TEAMS':

                team_grades_file = request.FILES['team_grades_file']
                print('team_grades_file',team_grades_file)

                file_name = default_storage.save('./static/grades/teams/'+team_grades_file.name, team_grades_file)

                messages.info(request,"Teams File Saved Successfully! Please Wait until the grades upload..")

                import_grades('./static/grades/teams/'+team_grades_file.name , 'TEAMS')

                messages.info(request,"Teams Grades Uploaded Successfully!!!")

                os.remove(os.path.join('./static/grades/teams/'+team_grades_file.name))
            else:

                repel_grades_file = request.FILES['repel_grades_file']
                print('repel_grades_file',repel_grades_file)

                file_name = default_storage.save('./static/grades/repel/'+repel_grades_file.name, repel_grades_file)

                messages.info(request,"Repl File Saved Successfully! Please Wait until the grades upload..")

                import_grades('./static/grades/repel/'+repel_grades_file.name , 'REPL')

                messages.info(request,"Repel Grades Uploaded Successfully!!!")

                os.remove(os.path.join('./static/grades/repel/'+repel_grades_file.name))

        cursor.execute(StudentsGradesQuery.format(pk))
        resultsList =  dictfetchall(cursor)
        return render(request,'assignments.html', {"resultsList":resultsList})

    else:
        return redirect('/login')

def assignments_summary(request):
    if request.user.is_authenticated :
        batch_info = Batch.objects.all()
        b_info = {"info" : batch_info}
        return render(request,'assignments-summary.html', b_info)

    else:
        return redirect('/login')

def create_batch(request , methods=['GET' , 'POST']):
    if request.user.is_authenticated :
        BatchCategory = Category.objects.all()
        BatchStatus = Status.objects.all()
        if request.method == "POST":
            cat_id = Category.objects.only('CategoryId').get(CategoryId=request.POST['batch_category'])
            sta_id = Status.objects.only('StatusId').get(StatusId=request.POST['batch_status'])
            batch = Batch(
                CategoryId = cat_id,
                BatchName = request.POST['batch_name'],
                BatchStartDate = request.POST['batch_start_date'],
                StatusId = sta_id
            )
            batch.save()
            messages.info(request,"Batch is Created......!!!!")

        
        return render(request,'create-batch.html',{'BatchCategory':BatchCategory , 'BatchStatus':BatchStatus})
    else:
        return redirect('/login')

def update_batch(request ,pk, methods=['GET' , 'POST']):
    if request.user.is_authenticated :
        Batch_Info = Batch.objects.filter(BatchId=pk)
        BatchCategory = Category.objects.all()
        BatchStatus = Status.objects.all()
        if request.method == "POST":
            cat_id = request.POST['batch_category']
            sta_id = request.POST['batch_status']
            sta_date = request.POST['batch_start_date']
            print('sta_date',sta_date)

            Batch_Info.update(BatchName = request.POST['batch_name'],CategoryId = cat_id, BatchStartDate = sta_date,BatchEndDate = request.POST['batch_end_date'],StatusId = sta_id)

        return render(request,'update-batch.html' , {'Batch_Info':Batch_Info , 'BatchStatus' : BatchStatus , 'BatchCategory' : BatchCategory})

    else:
        return redirect('/login')

def batch_students(request ,pk, methods=['GET' , 'POST']):
    if request.user.is_authenticated :
        
        Batch_Student = BatchStudent.objects.filter(BatchId=pk)
        Batch_i = Batch.objects.filter(BatchId=pk)
        my_group = Group.objects.get(name='Student') 
        

        

        Batch_Info = {'Batch_i':Batch_i}

        for i in Batch_Info['Batch_i']:
            stu_sta_date = i.BatchStartDate

        if request.method == "POST":

            if 'attendanceFile' in request.FILES :
                attendanceFile = request.FILES['attendanceFile']

                file_name = default_storage.save('./static/attendance/'+attendanceFile.name, attendanceFile)

                messages.info(request,"File Saved Successfully! Please Wait until the attendance upload..")

                upload_attendance_files(pk,filewithpath='./static/attendance/'+attendanceFile.name)

                messages.info(request,"Attendance Uploaded Successfully!!!")

                os.remove(os.path.join('./static/attendance/'+attendanceFile.name))

            else:

                import_file = request.FILES['import_file']

                file_name = default_storage.save('./static/importStudents/'+import_file.name, import_file)

                df = pd.read_csv('./static/importStudents/'+import_file.name)
                for i in df.index:
                    print('df' , df['email'][i])
                    if User.objects.filter(email=df['email'][i]).exists() :
                        print('email',df['email'][i])
                        pass
                    else:
                        print('in else' , df['email'][i])
                        student = Student(
                            StudentName=df['first_name'][i]+' '+df['last_name'][i],
                            StudentEmail=df['email'][i]
                            )
                        student.save()
                        user = User.objects.create_user(username=df['email'][i],
                                         first_name=df['first_name'][i],
                                         last_name=df['last_name'][i],
                                         email=df['email'][i],
                                         password=df['password'][i])

                        stu_id  = Student.objects.latest('StudentId')
                        us_id = User.objects.latest('id')
                        my_group.user_set.add(us_id)
                        batch_student = BatchStudent(
                            StartDate = stu_sta_date,
                            Status = df['status'][i],
                            BatchId = Batch.objects.only('BatchId').get(BatchId=pk),
                            StudentId = stu_id,
                            UserId = us_id
                            )
                        batch_student.save()

                messages.info(request,"Students are imported......!!!!")

                os.remove(os.path.join('./static/importStudents/'+import_file.name))

        
        return render(request,'batch-students.html' , {'Batch_Student':Batch_Student , 'Batch':Batch_i})

    else:
        return redirect('/login')
# here
def add_student(request ,pk, methods=['GET' , 'POST']):
    if request.user.is_authenticated :
        Batch_Student = BatchStudent.objects.filter(BatchId=pk)
        my_group = Group.objects.get(name='Student')
        # BatchCategory = Category.objects.all()
        # BatchStatus = Status.objects.all()
        if request.method == "POST":
            stu_f_name = request.POST['student_first_name']
            stu_l_name = request.POST['student_last_name']
            stu_email = request.POST['student_email']
            stu_password = request.POST['student_password']
            stu_sta_date = request.POST['start_date']
            stu_status = request.POST['student_status']
            stu_name = stu_f_name+' '+stu_l_name
            print("add_student")
            print(stu_name)
            student = Student(
                StudentName = stu_name,
                StudentEmail = stu_email
                )
            student.save()
            user = User.objects.create_user(username=stu_email,
                                 first_name=stu_f_name,
                                 last_name=stu_l_name,
                                 email=stu_email,
                                 password=stu_password)
            stu_id  = Student.objects.latest('StudentId')
            us_id = User.objects.latest('id')
            my_group.user_set.add(us_id)
            batch_student = BatchStudent(
                StartDate = stu_sta_date,
                Status = stu_status,
                BatchId = Batch.objects.only('BatchId').get(BatchId=pk),
                StudentId = stu_id,
                UserId = us_id
                )
            batch_student.save()
            messages.info(request,"Student is Added......!!!!")
        #     Batch_Info.update(BatchName = request.POST['batch_name'],CategoryId = cat_id, BatchStartDate = sta_date,BatchEndDate = request.POST['batch_end_date'],StatusId = sta_id)

        return render(request,'add-student.html' , {'Batch_Student':Batch_Student ,})

    else:
        return redirect('/login')

def transfer_student(request ,pk, methods=['GET' , 'POST']):
    if request.user.is_authenticated :
        Batch_List = Batch.objects.all()
        Batch_Student = BatchStudent.objects.filter(StudentId=pk)
        BS = {'Batch_Student' : Batch_Student}
        for i in BS['Batch_Student']:
            u_id = i.UserId.id
        if request.method == "POST":
            batch_name = request.POST['select_batch']
            stu_sta_date = request.POST['start_date']
            stu_status = request.POST['student_status']
            print('Batch Name : ',batch_name)
            print('Batch Date : ',stu_sta_date)
            print('Batch Status : ',stu_status)

            Batch_Student.update(EndDate = stu_sta_date,Status='Shifted to Another Batch')
            Batch_Student.create(StartDate=stu_sta_date,BatchId=Batch.objects.only('BatchId').get(BatchId=batch_name),StudentId=Student.objects.only('StudentId').get(StudentId=pk),UserId=User.objects.only('id').get(id=u_id),Status=stu_status)
            return redirect('/allStudents')

        return render(request,'transfer-student.html' , {'Batch_List':Batch_List})

    else:
        return redirect('/login')

def student_status_update(request ,pk, methods=['GET' , 'POST']):
    if request.user.is_authenticated :
        Batch_List = Batch.objects.all()
        Batch_Student = BatchStudent.objects.filter(StudentId=pk)
        BS = {'Batch_Student' : Batch_Student}
        for i in BS['Batch_Student']:
            u_id = i.UserId.id
        if request.method == "POST":
            stu_status = request.POST['student_status']
            print('Batch Status : ',stu_status)

            Batch_Student.update(Status = stu_status)
            return redirect('/allStudents')

        return render(request,'student_status-update.html' , {'Batch_List':Batch_List})

    else:
        return redirect('/login')
# here
def add_student_only(request , methods=['GET' , 'POST']):
    print("add_student_only_start")
    if request.user.is_authenticated :
        my_group = Group.objects.get(name='Student')
        print("add_student_only_is_authenticated")
        if request.method == "POST":
            print("add_student_only_method_POST")
            if 'import_file' in request.FILES :
                import_file = request.FILES['import_file']
                print('Got')
                file_name = default_storage.save('./static/importStudents/'+import_file.name, import_file)

                df = pd.read_csv('./static/importStudents/'+import_file.name)
                for i in df.index:
                    print('df' , df['email'][i])
                    if User.objects.filter(email=df['email'][i]).exists() :
                        print('email',df['email'][i])
                        pass

                    else:
                        student = Student(
                            StudentName=df['first_name'][i]+' '+df['last_name'][i],
                            StudentEmail=df['email'][i]
                            )
                        student.save()
                        user = User.objects.create_user(username=df['email'][i],
                                         first_name=df['first_name'][i],
                                         last_name=df['last_name'][i],
                                         email=df['email'][i],
                                         password=df['password'][i])
                        us_id = User.objects.latest('id')
                        my_group.user_set.add(us_id)

                messages.info(request,"Students are Imported......!!!!")
                os.remove(os.path.join('./static/importStudents/'+import_file.name))

            else:
            
                stu_f_name = request.POST['student_first_name']
                stu_l_name = request.POST['student_last_name']
                stu_email = request.POST['student_email']
                stu_pass = request.POST['student_password']
                stu_name = stu_f_name+' '+stu_l_name

                


                student = Student(
                    StudentName = stu_name,
                    StudentEmail = stu_email
                    )
                student.save()
                user = User.objects.create_user(username=stu_email,
                                     first_name=stu_f_name,
                                     last_name=stu_l_name,
                                     email=stu_email,
                                     password=stu_pass)
                us_id = User.objects.latest('id')
                my_group.user_set.add(us_id)
                
                messages.info(request,"Student is Added......!!!!")
   
        return render(request,'add-student-only.html')

    else:
        return redirect('/login')

def upload_attendance_only(request):
    if request.user.is_authenticated :
        Batch_Details = Batch.objects.all()
        if request.method == "POST":
            print("In Post")
            batch_id = request.POST.getlist('batches')
            print(batch_id)

            

            attendanceFile = request.FILES['attendanceFile']
            print(attendanceFile.name)

            file_name = default_storage.save('./static/attendance/'+attendanceFile.name, attendanceFile)

            messages.info(request,"File Saved Successfully! Please Wait until the attendance upload..")

            upload_attendance_files(filewithpath='./static/attendance/'+attendanceFile.name,multiplebatchid=batch_id)

            messages.info(request,"Attendance Uploaded Successfully!!!")

            os.remove(os.path.join('./static/attendance/'+attendanceFile.name))

        return render(request,'upload-attendance-only.html' , {"Batch_Details" : Batch_Details })

    else:

        return redirect('/login')
 
def student_notes(request ,pk, methods=['GET' , 'POST']):
    if request.user.is_authenticated :
        Batch_List = Batch.objects.all()
        Batch_Student = BatchStudent.objects.filter(StudentId=pk)
        if request.method == "POST":
            student_note = request.POST['student_note']
            notes_date = request.POST['notes_date']
            notes_editor = request.POST['notes_editor']
            print('Batch Name : ',student_note)
            print('Batch Date : ',notes_date)
            print('Batch Status : ',notes_editor)

            
            studentNotes = StudentNotes(
                StudentId =Student.objects.only('StudentId').get(StudentId=pk),
                NotesDate = notes_date,
                NotesDescription = student_note,
                NotesEditor = notes_editor
                )
            studentNotes.save()

            return redirect('/studentattendancedetails/'+str(pk))

        return render(request,'student-notes.html' , {'Batch_List':Batch_List})

    else:
        return redirect('/login')

#Student Details
def allStudents(request):
    if request.user.is_authenticated :
        cursor.execute(AllStudents)
        resultset =  dictfetchall(cursor)
        StudentDetails = BatchStudent.objects.all()

        return render(request,'all-students.html',{"StudentDetails" : StudentDetails , "resultset" : resultset})


def Teacherdetails(request):
    if request.user.is_authenticated and User.objects.filter(groups__name='Teacher').exists():
        # print("user.objects")
        print(User.objects.filter(groups__name='Teacher'))
        print("***********************")
        cursor.execute(AllTeacher)
        Teacher_cls_detail =  dictfetchall(cursor)
        
        s = {"Teacher_cls_detail":Teacher_cls_detail}
        print("s",s)
        return render(request,'all-teacher.html',s)

    else:
        return redirect('/login')

#see all users
@csrf_protect
def fetchitemsteacher(request):
    print('request.GET', request.GET)
    if request.method=="POST":
        id = request.POST['option']
        # batch_k = request.POST['batch_k']
        # print('batch_k',id)
        if id=='this week':
            cursor.execute(Teacher_attendance_lastweek) 
            results = cursor.fetchall()
            x = cursor.description
            resultsList = []   
            for r in results:
                i = 0
                d = {}
                while i < len(x):
                    d[x[i][0]] = r[i]
                    i = i+1
                resultsList.append(d)
            print('all_product',resultsList)
            
            return JsonResponse(resultsList, safe=False)

        elif id=='this month':
            cursor.execute(Teacher_attendance_lastmonth)
            results = cursor.fetchall()
            x = cursor.description
            #print('all_product',Session.objects.raw(StudentHighestPlacement))
            resultsList = []   
            for r in results:
                i = 0
                d = {}
                while i < len(x):
                    d[x[i][0]] = r[i]
                    i = i+1
                resultsList.append(d)
            print('all_product',resultsList)
            
            return JsonResponse(resultsList, safe=False)

        # else:
        #     cursor.execute(StudentAttendanceSummaryQuery.format(pk=batch_k))
        #     results = cursor.fetchall()
        #     x = cursor.description
        #     #print('all_product',Session.objects.raw(StudentHighestPlacement))
        #     resultsList = []   
        #     for r in results:
        #         i = 0
        #         d = {}
        #         while i < len(x):
        #             d[x[i][0]] = r[i]
        #             i = i+1
        #         resultsList.append(d)
        #     print('all_product',resultsList)
            
        #     return JsonResponse(resultsList, safe=False) 
        
            #print('all_product',Session.objects.raw(StudentHighestPlacement))



def teacherattendancedetails(request,pk):
    if request.user.is_authenticated and User.objects.filter(groups__name='Operation').exists() :
        # Teacherclass = Teacher_class_detail.objects.filter(UserId_id=pk)
        # cursor.execute(StudentAttendanceDetailsQuery.format(pk))
        # resultset =  dictfetchall(cursor)

        Teacherclass = Teacher_class_detail.objects.filter(UserID_id=pk)
        s = {"Teacher_cls_detail" : Teacherclass}
        
        return render(request,'teacher-attendance-details.html',s)

    else:
        return redirect('/login')

def raiseticket(request, methods=['GET' , 'POST']):
    if request.user.is_authenticated :
        ticket_List = ticketcategory.objects.all()
        ticket_List1 = ticketsubcategory.objects.all()
        ticket_List2 = ticketstatus.objects.all()
        
        
        TS = {'ticket_List' : ticket_List,'ticket_List1':ticket_List1}
        if request.method == "POST":
            std_id = request.user.id
            email = request.user
            fullname = request.user.first_name+" "+request.user.last_name
            cat = request.POST.get('question-subject')
            subcat = request.POST.getlist('question-topic')
            print(cat)
            print(int(subcat[0]))
            # category=ticketcategory.objects.only('ticketcategoryname').get(ticketcategoryname=cat)
            # subcategory=ticketsubcategory.objects.get(ticketsubcategoryname=subcat)
            category=ticketcategory.objects.filter(ticketcategoryid=cat)[0]
            subcategory=ticketsubcategory.objects.filter(ticketsubcategoryid=int(subcat[0]))[0]

            student_id = Student.objects.get(StudentId=std_id)
            assignuser = User.objects.get(username='admin')
            ticket_status = ticketstatus.objects.get(ticketstatusname='Not Assigned')
            issue = request.POST['student_issue']

            # print('category : ',category)
            # print('subcategory : ',subcategory)
            # print('issue : ',issue)


            obj = tickets(
                ticketdescription=issue,
                ticketcategory=category,
                ticketsubcategory=subcategory,
                studentid=student_id,
                assignedtouser = assignuser,
                ticketstatus = ticket_status,
                stdname = fullname,
                stdemail = email
                    )
            obj.save()
            messages.success(request, 'We have request your concern! and we will contact you soon.')
        return render(request,'raiseticket.html',TS)

    else:
        return redirect('/login')

def allStudentstickets(request):
    if request.user.is_authenticated and User.objects.filter(groups__name='Operation').exists():
        email = request.user
        fullname = request.user.first_name+" "+request.user.last_name
        ticket_data = tickets.objects.all().order_by('ticketid').reverse()
        ticket_List = ticketcategory.objects.all()
        ticket_List1 = ticketsubcategory.objects.all()
        ticket_List2 = ticketstatus.objects.all()
        print(ticket_data)
        context = {"ticket_List":ticket_List,
                    "ticket_List1":ticket_List1,
                    "ticket_List2":ticket_List2,
                    "email":email,
                    "fullname":fullname,
                    "ticket_data":ticket_data}


        return render(request,'all-studentstickets.html',context)

def ticket_status_update(request,pk, methods=['GET' , 'POST']):
    if request.user.is_authenticated :

        ticketdesc = tickets.objects.filter(ticketid=pk)
        cursor.execute(operationuserforticket.format(ticketid=pk))  
        tkt_assign =  dictfetchall(cursor)
        # print(tkt_assign)
        cursor.execute(statusforticket.format(ticketid=pk))  
        mystatus =  dictfetchall(cursor)
       
        if request.method == "POST":
            tkt_status = request.POST.get('ticket_status')
            tkt_status1 = int(request.POST.get('ticket_status1'))
            ticketdesc = request.POST.get('ticketdescription')
            
            t = tickets.objects.filter(ticketid=pk)
            x = ticketstatus.objects.get(ticketstatusid=tkt_status)
            y = User.objects.only('id').get(id=tkt_status1)
          
            t.update(
                ticketstatus=x,
                assignedtouser=tkt_status1,
                lastmodifieddate = datetime.now(),
                ticketdescription = ticketdesc
                )
          
            return redirect('/allStudentstickets')

        print(ticketdesc)
        return render(request,'ticket_status-update.html' , {'tkt_assign':tkt_assign,'mystatus':mystatus,'ticketdesc':ticketdesc})

    else:
        return redirect('/login')

def getcategoryajax(request):
    if request.method == "POST":
        subject_id = request.POST['subjectId']
        print(subject_id)
        # subject = ticketcategory.objects.filter(ticketcategoryid = subject_id).values()
        topics = ticketsubcategory.objects.filter(ticketcategoryid = subject_id).values_list()
        print(topics)
        print(list(topics.values('ticketsubcategoryid','ticketsubcategoryname')))
        return JsonResponse(list(topics.values('ticketsubcategoryid','ticketsubcategoryname')), safe = False)

# def getBatchcategoryajax(request):
#     if request.method == "POST":
#         batchId_id = request.POST['batchId']
#         print(batchId_id)
#         # subject = ticketcategory.objects.filter(ticketcategoryid = subject_id).values()
#         batch = Batch.objects.filter(BatchId = batchId_id).values_list()
#         print(batch)
#         print(list(batch.values('BatchId','BatchName')))
#         return JsonResponse(list(batch.values('BatchId','BatchName')), safe = False)




@api_view(['Post'])
def save_createmeetings(request):
    data = request.data
    serializer = CreatemeetingsSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
        'status':200,
        'data':serializer.data,
        'message':'data save succesfully'
        })
    else:
        return Response({
        'status':404,
        'data':serializer.errors,
        'message':'something went wrong'
        })

# -------------------------------------------

# <HomeViewSnippet>
def home1(request):
  context = initialize_context(request)

  return render(request, 'tutorial/home.html', context)
# </HomeViewSnippet>

# <InitializeContextSnippet>
def initialize_context(request):
    context = {}
    print(request)
    
    # Print session information
    print("Session:", request.session)
    
    # Check for any errors in the session
    error = request.session.pop('flash_error', None)

    if error != None:
        context['errors'] = []
        context['errors'].append(error)

    # Check for user in the session
    user = request.session.get('user', {'is_authenticated': False})
    print("User:", user)  # Print user information
    context['user'] = user
    
    return context

# </InitializeContextSnippet>

# <SignInViewSnippet>
def sign_in(request):
  # Get the sign-in flow
  flow = get_sign_in_flow()
  # Save the expected flow so we can use it in the callback
  try:
    request.session['auth_flow'] = flow
  except Exception as e:
    print(e)
  # Redirect to the Azure sign-in page
  return HttpResponseRedirect(flow['auth_uri'])
# </SignInViewSnippet>

# <SignOutViewSnippet>
def sign_out(request):
  # Clear out the user and token
  remove_user_and_token(request)

  return HttpResponseRedirect(reverse('home1'))
# </SignOutViewSnippet>

# <CallbackViewSnippet>
def callback(request):
  # Make the token request
  result = get_token_from_code(request)

  #Get the user's profile
  user = get_user(result['access_token'])
  x = access_token(request)
  obj = mycelerytask(access_token=x)
  obj.save()

  # Store user
  store_user(request, user)
  return HttpResponseRedirect(reverse('home1'))
# </CallbackViewSnippet>

# <CalendarViewSnippet>
def calendar(request):
  context = initialize_context(request)
  user = context['user']

  # Load the user's time zone
  # Microsoft Graph can return the user's time zone as either
  # a Windows time zone name or an IANA time zone identifier
  # Python datetime requires IANA, so convert Windows to IANA
  time_zone = get_iana_from_windows(user['timeZone'])
  tz_info = tz.gettz(time_zone)

  # Get midnight today in user's time zone
  today = datetime.now(tz_info).replace(
    hour=0,
    minute=0,
    second=0,
    microsecond=0)

  # Based on today, get the start of the week (Sunday)
  if (today.weekday() != 6):
    start = today - timedelta(days=today.isoweekday())
  else:
    start = today

  end = start + timedelta(days=7)

  token = get_token(request)

  events = get_calendar_events(
    token,
    start.isoformat(timespec='seconds'),
    end.isoformat(timespec='seconds'),
    user['timeZone'])

  if events:
    # Convert the ISO 8601 date times to a datetime object
    # This allows the Django template to format the value nicely
    for event in events['value']:
      event['start']['dateTime'] = parser.parse(event['start']['dateTime'])
      event['end']['dateTime'] = parser.parse(event['end']['dateTime'])

    context['events'] = events['value']

  return render(request, 'tutorial/calendar.html', context)
# </CalendarViewSnippet>

# <NewEventViewSnippet>
def newevent(request):
  context = initialize_context(request)
  batches = Batch.objects.all().values()
  print("****************************")
  print(context)
  print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
  user = context['user']

  if request.method == 'POST':
    # Validate the form values
    # Required values
    if (not request.POST['ev-subject']) or \
       (not request.POST['ev-start']) or \
       (not request.POST['ev-end']):
      context['errors'] = [
        { 'message': 'Invalid values', 'debug': 'The subject, start, and end fields are required.'}
      ]
      return render(request, 'tutorial/newevent.html', context)

    attendees = None
    if request.POST['ev-attendees']:
      attendees = request.POST['ev-attendees'].split(';')
    body = request.POST['ev-body']

    # Create the event
    token = get_token(request)

    event_data = create_event(
      token,
      request.POST['ev-subject'],
      request.POST['ev-start'],
      request.POST['ev-end'],
      attendees,
      request.POST['ev-body'],
      user['timeZone'])

    if request.method == 'POST':
        batchval  = request.POST['batchval']
        batch_id = batchval.split(';')
        new = [i for i in batch_id if i]
        s = []
        if len(new)<1:
            x = int(new[0])
            s.append(x)
        else:
            for i in new:
                y = int(i)
                s.append(y)
        for i in s:
            obj = batchmeeting(Batchid=i)
            obj.save()
   

    # print(event_data)
    # meetingurl = event_data['onlineMeeting']['joinUrl']
    # print(meetingurl)

    # headers = {'Authorization':'Bearer'}
    # token = get_token(request)
    # #   print(token)
    # headers = {
    #     'Authorization': 'Bearer {0}'.format(token),
    #     'Content-Type': 'application/json'
    # }
    # endpoint = 'https://graph.microsoft.com/v1.0/me/onlineMeetings/?$filter=JoinWebUrl+eq+'+"'"+meetingurl+"'"
    # data = json.loads(requests.get(endpoint,headers=headers).text)
    # print(data)
    # import time
    
    # meeting_id = data['value'][0]['id']
    # print(meeting_id)
    # import re
    # pattern = re.compile(r'\(([^)]*)\)')

    # s = data['@odata.context']
    # userid = pattern.findall(s)[0].split("'")[1]
    # print(userid)

    # endpoint = "https://graph.microsoft.com/v1.0/users/" + userid +"/onlineMeetings/" +meeting_id+"/attendanceReports"
    # print(endpoint)
    # data1 = json.loads(requests.get(endpoint,headers=headers).text)
    # print(data1)
    # time.sleep(120)
    # attendanceReportsid = data1['value'][0]['id']
    # endpoint1 = endpoint + attendanceReportsid + "/attendanceRecords"
    # attendence_data= json.loads(requests.get(endpoint1,headers=headers).text)
    # Organizer_attendence = attendence_data['value'][0]['totalAttendanceInSeconds']
    # Organizer_name = attendence_data['value'][0]['identity']['displayName']
    # Organizer_jointime = attendence_data['value'][0]['attendanceIntervals'][0]['joinDateTime']
    # Organizer_leavetime = attendence_data['value'][0]['attendanceIntervals'][0]['leaveDateTime']
    # import pandas as pd
    # df_name = pd.DataFrame(data = [Organizer_name],columns=["name"])
    # df_attendence = pd.DataFrame(data = [Organizer_attendence],columns=["attendenceInseconds"])
    # df_jointime = pd.DataFrame(data = [Organizer_jointime],columns=["jointime"])
    # df_leavetime = pd.DataFrame(data = [Organizer_leavetime],columns=["leavetime"])
    # df = pd.concat([df_name,df_jointime,df_leavetime,df_attendence,],axis=1)
    # df.to_csv('attendence.csv')

    # Redirect back to calendar view
    return HttpResponseRedirect(reverse('calendar'))
  else:
    # Render the form
    return render(request, 'create_new_meetings.html',{'batches':batches})
    
# </NewEventViewSnippet>

def access_token(request):
    return get_token(request)

def education(request):
  import json
  context = initialize_context(request)
  x = access_token(request)
#   obj = mycelerytask(access_token=x)
#   obj.save()
#   y = mycelerytask.objects.all().values().order_by('-mytaskId')[0]
#   print(y)

#   print(obj)
  api_data = task.add_api_data.delay(access_token(request))
#   celery_task = celerytask(celery_task_id = api_data.id,status = AsyncResult(request.id).status)

#   celery_task.save() # added save line
#   print(api_data)
#   api_delete_data = task.delete_api_data.delay()
  api_list = assignment_data.objects.all().values()
#   print(api_list)
#   tasklist = celerytask.objects.all().values()
#   print(api_list)
  return render(request, 'tutorial/task.html', {'context':context})

def mytask(request):
  context = initialize_context(request)
#   x = access_token(request)
#   obj = mycelerytask(access_token=x)
#   obj.save()
#   x = mycelerytask.objects.all().values().order_by('-mytaskId')[0]
#   print(x)
  return render(request, 'tutorial/task.html', context)


def newgrade(request):
  context = initialize_context(request)
  return render(request, 'tutorial/grade.html', context)


def test(request):
  context = initialize_context(request)
  return render(request, 'test.html', context)

# <NewmeetingSnippet>
def onlinemeeting(request):
  context = initialize_context(request)
  user = context['user']
      # Create the event
  token = get_token(request)
  headers = {
        'Authorization': 'Bearer {0}'.format(token),
        'Content-Type': 'application/json'
    }

  if request.method == 'POST':
    # Validate the form values
    # Required values
    if (not request.POST['ev-subject']) or \
       (not request.POST['ev-start']) or \
       (not request.POST['ev-end']):
      context['errors'] = [
        { 'message': 'Invalid values', 'debug': 'The subject, start, and end fields are required.'}
      ]
      return render(request, 'new_meetings.html', context)
    #   return render(request, 'newevent.html', context)




    data = create_onlinemeetings(
      token,
      request.POST['ev-subject'],
      request.POST['ev-start'],
      request.POST['ev-end'])

    # meeting_id = data['id']
    # print(meeting_id)
    # import re
    # pattern = re.compile(r'\(([^)]*)\)')

    # s = data['@odata.context']
    # userid = pattern.findall(s)[0].split("'")[1]
    # print(userid)

    # endpoint = "https://graph.microsoft.com/v1.0/users/" + userid +"/onlineMeetings/" +meeting_id+"/attendanceReports"
    # print(endpoint)
    # data1 = requests.get(endpoint,headers=headers).text
    # print(data1)
    # attendanceReportsid = data1['id']
    # endpoint1 = endpoint + attendanceReportsid + "/attendanceRecords"
    # attendence_data= requests.get(endpoint1,headers=headers).text
    # Organizer_attendence = attendence_data['value'][0]['totalAttendanceInSeconds']
    # Organizer_name = attendence_data['value'][0]['identity']['displayName']
    # Organizer_jointime = attendence_data['value'][0]['attendanceIntervals'][0]['joinDateTime']
    # Organizer_leavetime = attendence_data['value'][0]['attendanceIntervals'][0]['leaveDateTime']
    # import pandas as pd
    # df_name = pd.DataFrame(data = [Organizer_name],columns=["name"])
    # df_attendence = pd.DataFrame(data = [Organizer_attendence],columns=["attendenceInseconds"])
    # df_jointime = pd.DataFrame(data = [Organizer_jointime],columns=["jointime"])
    # df_leavetime = pd.DataFrame(data = [Organizer_leavetime],columns=["leavetime"])
    # df = pd.concat([df_name,df_jointime,df_leavetime,df_attendence,],axis=1)
    # print(df)

    



    # import json
    # base_url = "https://graph.microsoft.com/v1.0/"

    # endpoint = base_url +'users'


    # Redirect back to calendar view
    return HttpResponseRedirect(reverse('calendar'))
  else:
    # Render the form
    return render(request, 'new_meetings.html', context)


def meeting_attendence(request):
  context = initialize_context(request)
#   meeting_data = task.add_meeting_attendence.delay(access_token(request))
  import json
#   graph api base url
  base_url = "https://graph.microsoft.com/v1.0/"
  endpoint = base_url +'me/events'
  headers = {'Authorization':'Bearer'}
  token = get_token(request)
#   print(token)
  headers = {
    'Authorization': 'Bearer {0}'.format(token),
    'Content-Type': 'application/json'
  }
  data = json.loads(requests.get(endpoint,headers=headers).text)
#   print(data)
  data_new = data['value']
  meetingjoinurl_list = []
  for i in range(len(data_new)):
    meetingjoinurl_list.append(data_new[i]['onlineMeeting']['joinUrl'])
  import re
  pattern = re.compile(r'\(([^)]*)\)')
  s = data['@odata.context']
  userid = pattern.findall(s)[0].split("'")[1]
  baseurl_attendence = "https://graph.microsoft.com/v1.0/users/"
  finaljoinurlmeetings_url = []
  for i in meetingjoinurl_list:
      endurl_attendence = baseurl_attendence + userid +"/onlineMeetings/"+"?$filter=JoinWebUrl+eq+"+"'"+i+"'"
      finaljoinurlmeetings_url.append(endurl_attendence)
  
  
  allmeetingsid = []
  sessionstartDateTime = []
  sessionendDateTime = []
  subject = []
  for i in finaljoinurlmeetings_url:
      data = json.loads(requests.get(i,headers=headers).text)
      try:
        data = data['value'][0]
        allmeetingsid.append(data['id'])
        sessionstartDateTime.append(data['startDateTime'])
        sessionendDateTime.append(data['endDateTime'])
        subject.append(data['subject'])
      except KeyError as e:
          print(e)
#   print(allmeetingsid)
#   print(sessionstartDateTime)
#   print(sessionendDateTime)
#   print(subject)
  allattendencedata_url = []
  allmeetingurlid = []

  totalParticipantCount = []
  for i in allmeetingsid:
      meetdata_url = baseurl_attendence + userid +"/onlineMeetings/" +i+"/attendanceReports"
      meetingurl = json.loads(requests.get(meetdata_url,headers=headers).text)['value']
      if not meetingurl:
          pass
      else:
          meetingurlid = meetingurl[0]['id']
          noofParticipantCount = int(meetingurl[0]['totalParticipantCount'])
          allmeetingurlid.append(meetingurlid)
          totalParticipantCount.append(noofParticipantCount)
          meetdata_urldata = meetdata_url+"/"+meetingurlid+"/attendanceRecords"
          allattendencedata_url.append(meetdata_urldata)

  allmeetingsdata = []
  for i in allattendencedata_url:
      meetingdata = json.loads(requests.get(i,headers=headers).text)
      meetingdata = meetingdata['value']
      allmeetingsdata.append(meetingdata)
  updateallmeetingsdata = [ele for ele in allmeetingsdata if ele != []]
  print(updateallmeetingsdata)
#   print(len(updateallmeetingsdata))
  userid = []
  username = []
  role = []
  useremail =[]
  durationInSeconds = []
  joinDateTime = []
  leaveDateTime = []
#   print(userid)
#   print(username)
#   print(role)
#   print(useremail)
#   print(durationInSeconds)
#   print(joinDateTime)
#   print(leaveDateTime)
  ned = []
  print(ned)
  for i in updateallmeetingsdata:
    print((len(i)))
    ned.append(len(i))
    for j in i:
        userid.append(j['id'])
        useremail.append(j['emailAddress'])
        role.append(j['role'])
        username.append(j['identity']['displayName'])
        joinDateTime.append(j['attendanceIntervals'][0]['joinDateTime'])
        leaveDateTime.append(j['attendanceIntervals'][0]['leaveDateTime'])
        durationInSeconds.append(j['attendanceIntervals'][0]['durationInSeconds'])

  import numpy as np
  sessionstartDateTime_ = np.repeat(sessionstartDateTime,ned)
  sessionendDateTime_ = np.repeat(sessionendDateTime,ned)
  subject_ = np.repeat(subject,ned)
  allmeetingurlid_ = np.repeat(allmeetingurlid,ned)
  totalParticipantCount_ = np.repeat(totalParticipantCount,ned)
  import pandas as pd
  df_id = pd.DataFrame(data = userid,columns=["id"])
  df_name = pd.DataFrame(data =username,columns=["name"])
  df_email = pd.DataFrame(data =useremail,columns=["email"])
  df_role = pd.DataFrame(data =role,columns=["role"])
  df_durationInSeconds = pd.DataFrame(data = durationInSeconds,columns=["durationInSeconds"])
  df_jointime = pd.DataFrame(data = joinDateTime,columns=["jointime"])
  df_leavetime = pd.DataFrame(data = leaveDateTime,columns=["leavetime"])
  df_sessionstartDateTime = pd.DataFrame(data = sessionstartDateTime_,columns=["sessionstartDateTime"])
  df_sessionendDateTime = pd.DataFrame(data = sessionendDateTime_,columns=["sessionendDateTime"])
  df_subject = pd.DataFrame(data = subject_,columns=["SessionName"])
  df_meetinghash = pd.DataFrame(data = allmeetingurlid_,columns=["meetinghash"])
  df_totalParticipantCount = pd.DataFrame(data = totalParticipantCount_,columns=["totalParticipantCount"])
  df = pd.concat([df_id,df_name,df_email,df_role,df_durationInSeconds,df_jointime,df_leavetime,df_sessionstartDateTime,df_sessionendDateTime,df_subject,df_meetinghash,df_totalParticipantCount],axis=1)
  print(df)
  from sqlalchemy import create_engine
  table_name = 'studentattendencedetails'
  engine = create_engine('sqlite:///db.sqlite3')
  # Code to create a new temp table here.
  new_df = df.to_sql(table_name, if_exists='replace', con=engine)

  conn = sqlite3.connect('db.sqlite3')
  cur = conn.cursor()
#   cur.execute("""SELECT * from portal_batchmeeting ORDER by id DESC LIMIT {val}""".format(val=len(allmeetingurlid)))
  cur.execute("""SELECT * from portal_batchmeeting ORDER by id DESC LIMIT {val}""".format(val=len(updateallmeetingsdata)))
  curr_batchid = cur.fetchall()
  for i in range(len(curr_batchid)):
    print(curr_batchid[i][1])
#   curr_batchid = cur.fetchall()[0][1]
#   print(curr_batchid)
    from django.db import IntegrityError
    try:
        # code that produces error
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute("""INSERT INTO portal_session(SessionStartDate,SessionEndDate,sessioncoordinateuser,noofparticipants,sessiontitle,sessionhash,batchid)
                        SELECT
                        studentattendencedetails.jointime,
                        studentattendencedetails.leavetime,
                        studentattendencedetails.email,
                        studentattendencedetails.totalParticipantCount,
                        studentattendencedetails.SessionName,
                        studentattendencedetails.meetinghash,
                        {batchid}

                        FROM studentattendencedetails JOIN auth_user 
                        on studentattendencedetails.email=auth_user.email
                        ;""".format(batchid=curr_batchid[i][1]))
        conn.commit()
    except IntegrityError as e:
        print(e)

    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    print(len(curr_batchid))
    cur.execute("""SELECT* FROM portal_session ORDER by portal_session.SessionId DESC LIMIT {limitval};""".format(limitval=len(curr_batchid)))
    # cur.execute("SELECT * from portal_session order by SessionId DESC LIMIT 1;")
    lastsessionid = cur.fetchall()
    print(lastsessionid)

    from django.db import IntegrityError
    try:
        # code that produces error
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute("""INSERT INTO portal_studentattendance(jointime,leavetime,duration,sessionid,studentid)
                                SELECT
                                STRFTIME('%Y-%m-%d %H:%M:%S', studentattendencedetails.jointime) as jointime,
                                STRFTIME('%Y-%m-%d %H:%M:%S', studentattendencedetails.leavetime) as leavetime,
                                studentattendencedetails.durationInSeconds,
                                {sessionid},
                                auth_user.id

                                FROM studentattendencedetails JOIN auth_user 
                                on studentattendencedetails.email=auth_user.email""".format(sessionid=lastsessionid[i][0]))
        conn.commit()
    except IntegrityError as e:
        print(e)

    from django.db import IntegrityError
    try:
        # code that produces error
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute("""INSERT INTO portal_teacher_class_detail(Teacherintime,Teacherouttime,teacher_duration,Teacher_name,Teacheremail,UserID_id)
                                        SELECT
                                        studentattendencedetails.jointime,
                                        studentattendencedetails.leavetime,
										time(studentattendencedetails.durationInSeconds, 'unixepoch') as duration,
                                        studentattendencedetails.name,
                                        studentattendencedetails.email,
                                        auth_user.id
  

                                        from studentattendencedetails JOIN auth_user on
                                        studentattendencedetails.role='Presenter'and lower(studentattendencedetails.email) = lower(auth_user.email)


                                        JOIN auth_user_groups on 
                                        auth_user_groups.id =auth_user.id where group_id=4""")
        conn.commit()
    except IntegrityError as e:
        print(e)

  return render(request, 'test.html', context)


