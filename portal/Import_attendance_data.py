from django.shortcuts import render
import pandas as pd

import sqlite3
from sqlite3 import IntegrityError
import pathlib

import sys
import string
import random
from datetime import datetime

import re

from requests import request
from django.http import HttpResponse

def calculateseconds(s):
    p_hour = re.compile('([0-9]+)h')
    p_min = re.compile('([0-9]+)m')
    p_sec = re.compile('([0-9]+)s')
    hours = re.search(p_hour,s)
    mins = re.search(p_min,s)
    secs = re.search(p_sec,s)
    totalsecs = 0
    if hours :
            totalsecs = totalsecs + int(hours.group(1))*3600
    if mins :
            totalsecs =  totalsecs + int(mins.group(1))*60
    if secs :
            totalsecs = totalsecs + int(secs.group(1))

    return totalsecs
                    


def strtodatetime(s):
    s = s.replace(',','')
    s = s.replace('/','-')
    if 'AM'  in s or 'PM' in s:
        return datetime.strptime(s,"%m-%d-%Y %I:%M:%S %p")
    else:
        return datetime.strptime(s,"%d-%m-%Y %H:%M:%S")
  

# def upload_attendance_files(batchId=None,filewithpath=None,dirpath=None,multiplebatchid=None):
#     conn = sqlite3.connect('db.sqlite3', timeout=30)

#     '''
#     Code for saving session information
#     '''    
#     if dirpath :
#         #Code for excel file
#         #files = list(pathlib.Path(dirpath).glob('*.xlsx'))
#         #Code for csv file
#         files = list(pathlib.Path(dirpath).glob('*.csv'))
    
#     if filewithpath :
#         files = [filewithpath]
   
#     if files :

#         print ("#######################################################")
#         print (" Import Module starts ")
#         print ("#######################################################")
#         print ('\n'*4)

#         for filepath in files:

#             """
#             Creating DataFrames for Session
#             """
#             # Code for excel file
#             #df = pd.read_excel(filepath , skiprows=1, nrows=5,header=None)

#             try:

#                 df = pd.read_csv(filepath , sep='\t' ,skiprows=1, nrows=6,header=None ,encoding='utf-16')
#                 # Code for excel file
#                 #df.columns  = ['property' , 'value', 'd1' , 'd2', 'd3', 'd4']
                
#                 df.columns  = ['property' , 'value']
#                 propertydf = df[['property', 'value']]

#                 # participants =  propertydf[propertydf["property"] == "Total Number of Participants"]["value"].values[0]
#                 # title = propertydf[propertydf["property"] == "Meeting Title"]["value"].values[0]
#                 # starttime = strtodatetime(propertydf[propertydf["property"] == "Meeting Start Time"]["value"].values[0])
#                 # endtime = strtodatetime(propertydf[propertydf["property"] == "Meeting End Time"]["value"].values[0])
#                 # mid= propertydf[propertydf["property"] == "Meeting Id"]["value"].values[0]

#                 title = df.iloc[0, 1]
#                 participants = df.iloc[1, 1]
#                 starttime = pd.to_datetime(df.iloc[2, 1])
#                 endtime = pd.to_datetime(df.iloc[3, 1])
#                 meeting_duration = df.iloc[4, 1]
#                 avg_attendance_time = df.iloc[5, 1]
#                 mid = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

#                 print("Summary:")
#                 print("Meeting title:", title)
#                 print("Attended participants:", participants)
#                 print("Start time:", starttime)
#                 print("End time:", endtime)
#                 print("meeting_duration:", meeting_duration)
#                 print("avg_attendance_time:", avg_attendance_time)
#                 print('Meeting id:', mid)
#                 #print (participants)
#                 #print (title)
#                 #print (starttime)
#                 #print (endtime)
#                 #print (mid)
#                 # Read Participants section
#                 # Read Participants section
#                 participants_df = pd.read_csv(filepath, skiprows=9, nrows=3, delimiter='\t',encoding='utf-16')
#                 print("****************************************************************************************************************************************************************************************************************************************************************")
#                 print("\nParticipants:")
#                 print(participants_df)
#                 print("****************************************************************************************************************************************************************************************************************************************************************")
#                 print("\nParticipants df columns:")
#                 print(participants_df.columns)

#                 # Read In-Meeting Activities section
#                 # activities_df = pd.read_csv(filepath, skiprows=15, delimiter='\t',encoding='utf-16')
#                 # print("\nIn-Meeting Activities:")
#                 # print(activities_df)
                

    
                


#                 """
#                 Creating DataFrame for Student
#                 """

#                 # Code for excel file
#                 #studentdf = pd.read_excel(filepath , skiprows=8,header=None) 

#                 studentdf = pd.read_csv(filepath, skiprows=9, nrows=3, delimiter='\t',encoding='utf-16')

#                 studentdf.columns = ['fullname', 'jointime'  , 'leavetime' , 'duration' , 'email' , 'role', 'Participant ID (UPN)']

#                 studentdf['duration'] = studentdf['duration'].apply(calculateseconds)

#                 studentdf.to_sql('temp_attendance_sheet', conn, schema=None, if_exists='replace', index=True, index_label=None, chunksize=None, dtype=None, method=None)

                

                

#                 #raise Exception("User defined")
                

#                 cur = conn.cursor()
                
#                 #Find if the session details already exist in the database
#                 cur.execute("select count(*) from portal_session where sessionhash = '{meetinghash}'".format(meetinghash = mid))

                

                
#                 checksessionexists = cur.fetchall()[0][0]
                
                
                
                
#                 # If the file is already processed then move to the next file in the loop
#                 if checksessionexists > 0:
#                     print ('The session data has already been imported for the file ', filepath)
#                     print ('...Moving to next file....')
#                     continue
                
                
#                 #Inserting data into the session table 
#                 if multiplebatchid:
#                     for i in multiplebatchid:
#                         query = """insert into portal_session (BatchId,SessionStartDate,SessionEndDate,sessioncoordinateuser,noofparticipants,sessiontitle,sessionhash,sessionfile)
#                                 values ( {batchid} ,'{p_starttime}' , '{p_endtime}' ,null, {p_participants} , '{p_title}' , '{p_mid}', '{p_filepath}')
#                                 """.format(batchid=i,p_starttime=starttime, p_endtime=endtime, p_participants=participants, p_title=title, p_mid=mid, p_filepath=filepath)
#                         cur.execute(query)
#                         '''
#                         Code for saving student attendance and student information
                        
#                         1. Get latest sessionid
#                         2. Save student info in student table if user is not present in auth_users table
#                         3. Save student attendance info in student attendance table if user is not present in auth table
#                         '''

#                         lastsessionid = cur.lastrowid


                        


#                         # Inserting data into student table for students which are not there already in student table of user table

#                         # studentcreatequery = """insert into portal_student (StudentName , StudentContact, Studentemail , StudentGender )
#                         # select distinct fullname , null , email , null from temp_attendance_sheet WHERE email not in
#                         # (select email from auth_user) and email not in (select StudentEmail from portal_student)"""

#                         # cur.execute(studentcreatequery)



#                         # Inserting data into attendance table as per latest session id

#                         attendancecreatequery = """insert into portal_studentattendance (StudentId,SessionId,JoinTime,LeaveTime,Duration)
#                         select portal_student.studentid  , {sessionid} , temp_attendance_sheet.jointime , temp_attendance_sheet.leavetime , temp_attendance_sheet.duration
#                         from temp_attendance_sheet join portal_student 
#                         on temp_attendance_sheet.email = portal_student.StudentEmail""".format(sessionid=lastsessionid)


#                         cur.execute(attendancecreatequery)

#                         try:
#                             conn = sqlite3.connect('db.sqlite3')
#                             cur = conn.cursor()
#                             cur.execute("""INSERT INTO portal_teacher_class_detail(Teacherintime,Teacherouttime,teacher_duration,Teacher_name,Teacheremail,UserID_id)
#                                         SELECT
#                                         temp_attendance_sheet.jointime,
#                                         temp_attendance_sheet.leavetime,
#                                         time(temp_attendance_sheet.duration, 'unixepoch') as duration,
#                                         temp_attendance_sheet.fullname,
#                                         temp_attendance_sheet.email,
#                                         auth_user.id,
                                        

#                                         from temp_attendance_sheet JOIN auth_user on
#                                         temp_attendance_sheet.role='Presenter'and lower(temp_attendance_sheet.email) = lower(auth_user.email)


#                                         JOIN auth_user_groups on 
#                                         auth_user_groups.id =auth_user.id where group_id=4""")
#                             conn.commit()
#                         except:
#                             print('error')


#                         # Update organizer info and teacherinfo in session table

#                         updatecoordinator = "update portal_session set sessioncoordinateuser = (select email from temp_attendance_sheet where role ='Organiser') where SessionId = {sessionid}".format(sessionid=lastsessionid)
#                         cur.execute(updatecoordinator)

#                         cur.execute("""select email from temp_attendance_sheet where temp_attendance_sheet.email in (
#                                        select auth_user.email from auth_user join auth_user_groups on auth_user.id = auth_user_groups.user_id 
#                                        join auth_group on auth_group.id = auth_user_groups.group_id
#                                        and auth_group.name = 'Instructor')""")
#                         res = cur.fetchall()

#                         if res:
#                            instructoremail = res[0][0]
#                            if instructoremail :
#                                cur.execute("Update portal_session set sessioninstructor = '{}'".format(instructoremail))
                        
#                         conn.commit()
#                         print ("Import done for file" , filepath)
                    
#                 else:
#                     print("batchId:", batchId)
#                     print("Attended participants:", participants)
#                     print("Start time:", starttime)
#                     print("End time:", endtime)
#                     print("title:", title)
#                     print("mid:", mid)
#                     print('filepath:', filepath)
#                     if not batchId :
#                         batchId = -1
#                     # Define your SQL query with parameter placeholders
#                     query = """INSERT INTO portal_session (BatchId, SessionStartDate, SessionEndDate, sessioncoordinateuser, noofparticipants, sessiontitle, sessionhash, sessionfile)
#                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

#                     # Tuple containing the parameter values
#                     params = (batchId, starttime.strftime('%Y-%m-%d %H:%M:%S'), endtime.strftime('%Y-%m-%d %H:%M:%S'), None, participants, title, mid, filepath)
#                     print("***************************************************************************")
#                     print(query)
#                     print("****************************************************************************")
#                     print(params)
#                     # Execute the query with parameters
#                     cur.execute(query, params)


#                     '''
#                     Code for saving student attendance and student information

#                     1. Get latest sessionid
#                     2. Save student info in student table if user is not present in auth_users table
#                     3. Save student attendance info in student attendance table if user is not present in auth table
#                     '''

#                     lastsessionid = cur.lastrowid


                    


#                     # Inserting data into student table for students which are not there already in student table of user table

#                     # studentcreatequery = """insert into portal_student (StudentName , StudentContact, Studentemail , StudentGender )
#                     # select distinct fullname , null , email , null from temp_attendance_sheet WHERE email not in
#                     # (select email from auth_user) and email not in (select StudentEmail from portal_student)"""

#                     # cur.execute(studentcreatequery)



#                     # Inserting data into attendance table as per latest session id

#                     attendancecreatequery = """insert into portal_studentattendance (StudentId,SessionId,JoinTime,LeaveTime,Duration)
#                     select portal_student.studentid  , {sessionid} , temp_attendance_sheet.jointime , temp_attendance_sheet.leavetime , temp_attendance_sheet.duration
#                      from temp_attendance_sheet join portal_student 
#                     on temp_attendance_sheet.email = portal_student.StudentEmail""".format(sessionid=lastsessionid)


#                     cur.execute(attendancecreatequery)

#                     try:
#                         conn = sqlite3.connect('db.sqlite3')
#                         cur = conn.cursor()
#                         cur.execute("""INSERT INTO portal_teacher_class_detail(Teacherintime,Teacherouttime,teacher_duration,Teacher_name,Teacheremail,UserID_id)
#                                     SELECT
#                                     temp_attendance_sheet.jointime,
#                                     temp_attendance_sheet.leavetime,
#                                     time(temp_attendance_sheet.duration, 'unixepoch') as duration,
#                                     temp_attendance_sheet.fullname,
#                                     temp_attendance_sheet.email,
#                                     auth_user.id,
                                    

#                                     from temp_attendance_sheet JOIN auth_user on
#                                     temp_attendance_sheet.role='Presenter'and lower(temp_attendance_sheet.email) = lower(auth_user.email)


#                                     JOIN auth_user_groups on 
#                                     auth_user_groups.id =auth_user.id where group_id=4""")
#                         conn.commit()
#                     except:
#                         print('error')

#                     # Update organizer info and teacherinfo in session table

#                     updatecoordinator = "update portal_session set sessioncoordinateuser = (select email from temp_attendance_sheet where role ='Organiser') where SessionId = {sessionid}".format(sessionid=lastsessionid)
#                     cur.execute(updatecoordinator)

#                     cur.execute("""select email from temp_attendance_sheet where temp_attendance_sheet.email in (
#                                    select auth_user.email from auth_user join auth_user_groups on auth_user.id = auth_user_groups.user_id 
#                                    join auth_group on auth_group.id = auth_user_groups.group_id
#                                    and auth_group.name = 'Instructor')""")
#                     res = cur.fetchall()

#                     if res:
#                        instructoremail = res[0][0]
#                        if instructoremail :
#                            cur.execute("Update portal_session set sessioninstructor = '{}'".format(instructoremail))
                    
#                     conn.commit()
#                     print ("Import done for file" , filepath)
            
#             except IndexError:
#                 df = pd.read_csv(filepath , sep='\t' ,skiprows=1, nrows=6,header=None ,encoding='utf-16')

#                 # Code for excel file
#                 #df.columns  = ['property' , 'value', 'd1' , 'd2', 'd3', 'd4']
                
#                 df.columns  = ['property' , 'value']
#                 propertydf = df[['property', 'value']]


#                 participants =  propertydf[propertydf["property"] == "Total Number of Participants"]["value"].values[0]
#                 title = propertydf[propertydf["property"] == "Meeting Title"]["value"].values[0]
#                 starttime = strtodatetime(propertydf[propertydf["property"] == "Meeting Start Time"]["value"].values[0])
#                 endtime = strtodatetime(propertydf[propertydf["property"] == "Meeting End Time"]["value"].values[0])
#                 mid= propertydf[propertydf["property"] == "Meeting Id"]["value"].values[0]



#                 #print (participants)
#                 #print (title)
#                 #print (starttime)
#                 #print (endtime)
#                 #print (mid)

                

    
                


#                 """
#                 Creating DataFrame for Student
#                 """

#                 # Code for excel file
#                 #studentdf = pd.read_excel(filepath , skiprows=8,header=None) 

#                 studentdf = pd.read_csv(filepath, skiprows=9, nrows=3, delimiter='\t',encoding='utf-16')

#                 studentdf.columns = ['fullname', 'jointime'  , 'leavetime' , 'duration' , 'email' , 'role', 'Participant ID (UPN)']

#                 studentdf['duration'] = studentdf['duration'].apply(calculateseconds)

#                 studentdf.to_sql('temp_attendance_sheet', conn, schema=None, if_exists='replace', index=True, index_label=None, chunksize=None, dtype=None, method=None)

                

                

#                 #raise Exception("User defined")
                

#                 cur = conn.cursor()
                
#                 #Find if the session details already exist in the database
#                 cur.execute("select count(*) from portal_session where sessionhash = '{meetinghash}'".format(meetinghash = mid))

                

                
#                 checksessionexists = cur.fetchall()[0][0]
                
                
                
                
#                 # If the file is already processed then move to the next file in the loop
#                 if checksessionexists > 0:
#                     print ('The session data has already been imported for the file ', filepath)
#                     print ('...Moving to next file....')
#                     continue
                
                
#                 #Inserting data into the session table 
#                 if multiplebatchid:
#                     for i in multiplebatchid:
#                         query = """insert into portal_session (BatchId,SessionStartDate,SessionEndDate,sessioncoordinateuser,noofparticipants,sessiontitle,sessionhash,sessionfile)
#                                 values ( {batchid} ,'{p_starttime}' , '{p_endtime}' ,null, {p_participants} , '{p_title}' , '{p_mid}', '{p_filepath}')
#                                 """.format(batchid=i,p_starttime=starttime, p_endtime=endtime, p_participants=participants, p_title=title, p_mid=mid, p_filepath=filepath)
#                         cur.execute(query)
#                         '''
#                         Code for saving student attendance and student information

#                         1. Get latest sessionid
#                         2. Save student info in student table if user is not present in auth_users table
#                         3. Save student attendance info in student attendance table if user is not present in auth table
#                         '''

#                         lastsessionid = cur.lastrowid


                        


#                         # Inserting data into student table for students which are not there already in student table of user table

#                         # studentcreatequery = """insert into portal_student (StudentName , StudentContact, Studentemail , StudentGender )
#                         # select distinct fullname , null , email , null from temp_attendance_sheet WHERE email not in
#                         # (select email from auth_user) and email not in (select StudentEmail from portal_student)"""

#                         # cur.execute(studentcreatequery)



#                         # Inserting data into attendance table as per latest session id

#                         attendancecreatequery = """insert into portal_studentattendance (StudentId,SessionId,JoinTime,LeaveTime,Duration)
#                         select portal_student.studentid  , {sessionid} , temp_attendance_sheet.jointime , temp_attendance_sheet.leavetime , temp_attendance_sheet.duration
#                          from temp_attendance_sheet join portal_student 
#                         on temp_attendance_sheet.email = portal_student.StudentEmail""".format(sessionid=lastsessionid)


#                         cur.execute(attendancecreatequery)

#                         try:
#                             conn = sqlite3.connect('db.sqlite3')
#                             cur = conn.cursor()
#                             cur.execute("""INSERT INTO portal_teacher_class_detail(Teacherintime,Teacherouttime,teacher_duration,Teacher_name,Teacheremail,UserID_id)
#                                         SELECT
#                                         temp_attendance_sheet.jointime,
#                                         temp_attendance_sheet.leavetime,
#                                         time(temp_attendance_sheet.duration, 'unixepoch') as duration,
#                                         temp_attendance_sheet.fullname,
#                                         temp_attendance_sheet.email,
#                                         auth_user.id,
  

#                                         from temp_attendance_sheet JOIN auth_user on
#                                         temp_attendance_sheet.role='Presenter'and lower(temp_attendance_sheet.email) = lower(auth_user.email)


#                                         JOIN auth_user_groups on 
#                                         auth_user_groups.id =auth_user.id where group_id=4""")
#                             conn.commit()
#                         except:
#                             print('error')


#                         # Update organizer info and teacherinfo in session table

#                         updatecoordinator = "update portal_session set sessioncoordinateuser = (select email from temp_attendance_sheet where role ='Organiser') where SessionId = {sessionid}".format(sessionid=lastsessionid)
#                         cur.execute(updatecoordinator)

#                         cur.execute("""select email from temp_attendance_sheet where temp_attendance_sheet.email in (
#                                        select auth_user.email from auth_user join auth_user_groups on auth_user.id = auth_user_groups.user_id 
#                                        join auth_group on auth_group.id = auth_user_groups.group_id
#                                        and auth_group.name = 'Instructor')""")
#                         res = cur.fetchall()

#                         if res:
#                            instructoremail = res[0][0]
#                            if instructoremail :
#                                cur.execute("Update portal_session set sessioninstructor = '{}'".format(instructoremail))
                        
#                         conn.commit()
#                         print ("Import done for file" , filepath)

                    
#                 else:
#                     if not batchId :
#                         batchId = -1
#                     query = """insert into portal_session (BatchId,SessionStartDate,SessionEndDate,sessioncoordinateuser,noofparticipants,sessiontitle,sessionhash,sessionfile)
#                                 values ( {batchid} ,'{p_starttime}' , '{p_endtime}' ,null, {p_participants} , '{p_title}' , '{p_mid}', '{p_filepath}')
#                                 """.format(batchid=batchId,p_starttime=starttime, p_endtime=endtime, p_participants=participants, p_title=title, p_mid=mid, p_filepath=filepath)
#                     cur.execute(query)


#                     '''
#                     Code for saving student attendance and student information

#                     1. Get latest sessionid
#                     2. Save student info in student table if user is not present in auth_users table
#                     3. Save student attendance info in student attendance table if user is not present in auth table
#                     '''

#                     lastsessionid = cur.lastrowid


                    


#                     # Inserting data into student table for students which are not there already in student table of user table

#                     # studentcreatequery = """insert into portal_student (StudentName , StudentContact, Studentemail , StudentGender )
#                     # select distinct fullname , null , email , null from temp_attendance_sheet WHERE email not in
#                     # (select email from auth_user) and email not in (select StudentEmail from portal_student)"""

#                     # cur.execute(studentcreatequery)



#                     # Inserting data into attendance table as per latest session id

#                     attendancecreatequery = """insert into portal_studentattendance (StudentId,SessionId,JoinTime,LeaveTime,Duration)
#                     select portal_student.studentid  , {sessionid} , temp_attendance_sheet.jointime , temp_attendance_sheet.leavetime , temp_attendance_sheet.duration
#                      from temp_attendance_sheet join portal_student 
#                     on temp_attendance_sheet.email = portal_student.StudentEmail""".format(sessionid=lastsessionid)


#                     cur.execute(attendancecreatequery)
#                     try:
#                         conn = sqlite3.connect('db.sqlite3')
#                         cur = conn.cursor()
#                         cur.execute("""INSERT INTO portal_teacher_class_detail(Teacherintime,Teacherouttime,teacher_duration,Teacher_name,Teacheremail,UserID_id)
#                                     SELECT
#                                     temp_attendance_sheet.jointime,
#                                     temp_attendance_sheet.leavetime,
#                                     time(temp_attendance_sheet.duration, 'unixepoch') as duration,
#                                     temp_attendance_sheet.fullname,
#                                     temp_attendance_sheet.email,
#                                     auth_user.id,
                               

#                                     from temp_attendance_sheet JOIN auth_user on
#                                     temp_attendance_sheet.role='Presenter'and lower(temp_attendance_sheet.email) = lower(auth_user.email)


#                                     JOIN auth_user_groups on 
#                                     auth_user_groups.id =auth_user.id where group_id=4""")
#                         conn.commit()
#                     except:
#                         print('error')


#                     # Update organizer info and teacherinfo in session table

#                     updatecoordinator = "update portal_session set sessioncoordinateuser = (select email from temp_attendance_sheet where role ='Organiser') where SessionId = {sessionid}".format(sessionid=lastsessionid)
#                     cur.execute(updatecoordinator)

#                     cur.execute("""select email from temp_attendance_sheet where temp_attendance_sheet.email in (
#                                    select auth_user.email from auth_user join auth_user_groups on auth_user.id = auth_user_groups.user_id 
#                                    join auth_group on auth_group.id = auth_user_groups.group_id
#                                    and auth_group.name = 'Instructor')""")
#                     res = cur.fetchall()

#                     if res:
#                        instructoremail = res[0][0]
#                        if instructoremail :
#                            cur.execute("Update portal_session set sessioninstructor = '{}'".format(instructoremail))
                    
#                     conn.commit()
#                     print ("Import done for file" , filepath)



#             except Exception as e:
#                 print ("Import failed for file ", filepath, "...Please check the error msg..")
#                 print ("\n"*2)
#                 print ("****Error msg starts***********")
#                 print(sys.exc_info()[0])
#                 print(sys.exc_info()[1])
#                 print(sys.exc_info()[2])
#                 print (type(e).__name__)
#                 print('line no : ',e.__traceback__.tb_lineno)
#                 print ("****Error msg end***********")
#                 print ("\n"*2)

#         print ('\n'*4)
#         print ("#######################################################")
#         print (" Import Module ends ")
#         print ("#######################################################")
#         conn.close()

    

# # if __name__=="__main__":
# #     upload_attendance_files(dirpath = r'C:\BCT\Digikull\Portal\testing\testdir')
# #     conn.close()
#     from django.db import IntegrityError

#     try:
#         # code that produces error
#         conn = sqlite3.connect('db.sqlite3')
#         cur = conn.cursor()
#         cur.execute("""INSERT INTO portal_teacher_class_detail(Teacherintime,Teacherouttime,teacher_duration,Teacher_name,Teacheremail,UserID_id)
#                     SELECT
#                     temp_attendance_sheet.jointime,
#                     temp_attendance_sheet.leavetime,
#                     time(temp_attendance_sheet.duration, 'unixepoch') as duration,
#                     temp_attendance_sheet.fullname,
#                     temp_attendance_sheet.email,
#                     auth_user.id

#                     from temp_attendance_sheet JOIN auth_user on
#                     temp_attendance_sheet.role='Presenter'and lower(temp_attendance_sheet.email) = lower(auth_user.email)


#                     JOIN auth_user_groups on 
#                     auth_user_groups.id =auth_user.id where group_id=4""")
#         conn.commit()
#     except IntegrityError as e:
#         return render(request,"template.html", {"message": e.message})

def upload_attendance_files(batchId=None, filewithpath=None, dirpath=None, multiplebatchid=None):
    print("Starting upload_attendance_files function...")

    conn = sqlite3.connect('db.sqlite3', timeout=30)
    print("Connected to SQLite database.")
    # Print batchId if it's not None
    if batchId:
        print("Batch ID:", batchId)

    if dirpath:
        files = list(pathlib.Path(dirpath).glob('*.csv'))
        print("Files found in directory:", files)
    
    if filewithpath:
        files = [filewithpath]
        print("File with path provided:", files)

    if files:
        for filepath in files:
            try:
                print("Processing file:", filepath)
                
                df = pd.read_csv(filepath , sep='\t', skiprows=1, nrows=6, header=None, encoding='utf-16')

                title = df.iloc[0, 1]
                participants = df.iloc[1, 1]
                starttime = pd.to_datetime(df.iloc[2, 1])
                endtime = pd.to_datetime(df.iloc[3, 1])
                meeting_duration = df.iloc[4, 1]
                avg_attendance_time = df.iloc[5, 1]
                mid = f"{batchId}_{starttime.strftime('%Y%m%d_%H%M%S')}"
                print("Title:", title)
                print("Participants:", participants)
                print("Start Time:", starttime)
                print("End Time:", endtime)
                print("Meeting Duration:", meeting_duration)
                print("Average Attendance Time:", avg_attendance_time)
                print("Meeting ID (mid):", mid)

                # Read the CSV file skipping the first 9 rows
                sdf = pd.read_csv(filepath, sep='\t', skiprows=9, header=None, encoding='utf-16')

                # Initialize an empty list to store participant data
                student_data = []

                # Iterate through the rows of the DataFrame
                # Iterate through the rows of the DataFrame
                for idx, row in sdf.iterrows():
                    # Check if the row is empty (all values are NaN) or contains meeting activities
                    if row.isnull().all() or "In-Meeting Activities" in row[0]:
                        # Break the loop if an empty row or meeting activities row is encountered
                        break
                    # Append the row to the participant data list
                    student_data.append(row)

                # Convert the participant data list into a DataFrame
                student_df = pd.DataFrame(student_data)

                # Set column names
                student_df.columns = ['fullname', 'jointime', 'leavetime', 'duration', 'email', 'Participant ID (UPN)', 'role']

                # Skip the first row as it contains column names
                student_df = student_df.iloc[1:]

                # Convert relevant columns to string data type
                student_df = student_df.astype(str)

                # Apply the calculateseconds function to the 'duration' column
                student_df['duration'] = student_df['duration'].apply(calculateseconds)

                print("Student data loaded from file:")
                print(student_df)

                # Insert student data into temporary table
                student_df.to_sql('temp_attendance_sheet', conn, schema=None, if_exists='replace', index=True, index_label=None, chunksize=None, dtype=None, method=None)
                print("Student data inserted into temporary table.")

                # Fetch and print data from temporary table
                temp_df = pd.read_sql('SELECT * FROM temp_attendance_sheet', conn)
                print("Data in temporary table:")
                print(temp_df)

                cur = conn.cursor()
                cur.execute("select count(*) from portal_session where sessionhash = '{meetinghash}'".format(meetinghash=mid))
                checksessionexists = cur.fetchall()[0][0]
                print("Number of existing sessions with hash", mid, ":", checksessionexists)

                # Continue processing if session doesn't exist
                if checksessionexists > 0:
                    continue

                # Insert session data
                if multiplebatchid:
                    for i in multiplebatchid:
                        query = """INSERT INTO portal_session (BatchId, SessionStartDate, SessionEndDate, sessioncoordinateuser, noofparticipants, sessiontitle, sessionhash, sessionfile)
           VALUES (?, ?, ?, null, ?, ?, ?, ?)"""
                        params = (i, starttime.strftime('%Y-%m-%d %H:%M:%S'), endtime.strftime('%Y-%m-%d %H:%M:%S'), participants, title, mid, filepath)
                        cur.execute(query, params)
                        lastsessionid = cur.lastrowid
                        print("Session data inserted with SessionId:", lastsessionid)

                        # Insert attendance data
                        attendancecreatequery = """insert into portal_studentattendance (StudentId,SessionId,JoinTime,LeaveTime,Duration)
                        select portal_student.studentid  , {sessionid} , temp_attendance_sheet.jointime , temp_attendance_sheet.leavetime , temp_attendance_sheet.duration
                         from temp_attendance_sheet join portal_student 
                        on temp_attendance_sheet.email = portal_student.StudentEmail""".format(sessionid=lastsessionid)
                        cur.execute(attendancecreatequery)
                        print("Attendance data inserted for SessionId:", lastsessionid)

                        try:
                            # Insert teacher/class details
                            cur.execute("""INSERT INTO portal_teacher_class_detail(Teacherintime,Teacherouttime,teacher_duration,Teacher_name,Teacheremail,UserID_id)
                                        SELECT
                                        temp_attendance_sheet.jointime,
                                        temp_attendance_sheet.leavetime,
                                        time(temp_attendance_sheet.duration, 'unixepoch') as duration,
                                        temp_attendance_sheet.fullname,
                                        temp_attendance_sheet.email,
                                        auth_user.id
                                        from temp_attendance_sheet JOIN auth_user on
                                        temp_attendance_sheet.role='Organizer'and lower(temp_attendance_sheet.email) = lower(auth_user.email)
                                        JOIN auth_user_groups on 
                                        auth_user_groups.user_id =auth_user.id where group_id=4""")
                            conn.commit()
                            print("Teacher/class details inserted.")
                        except:
                            pass

                        updatecoordinator = "update portal_session set sessioncoordinateuser = (select email from temp_attendance_sheet where role ='Organiser') where SessionId = {sessionid}".format(sessionid=lastsessionid)
                        cur.execute(updatecoordinator)
                        print("Coordinator updated for SessionId:", lastsessionid)

                        cur.execute("""select email from temp_attendance_sheet where temp_attendance_sheet.email in (
                                       select auth_user.email from auth_user join auth_user_groups on auth_user.id = auth_user_groups.user_id 
                                       join auth_group on auth_group.id = auth_user_groups.group_id
                                       and auth_group.name = 'Instructor')""")
                        res = cur.fetchall()

                        if res:
                            instructoremail = res[0][0]
                            if instructoremail:
                                cur.execute("Update portal_session set sessioninstructor = '{}'".format(instructoremail))
                                print("Instructor updated for SessionId:", lastsessionid)

                        conn.commit()
                    
                else:
                    if not batchId:
                        batchId = -1
                    query = """INSERT INTO portal_session (BatchId, SessionStartDate, SessionEndDate, sessioncoordinateuser, noofparticipants, sessiontitle, sessionhash, sessionfile)
           VALUES (?, ?, ?, null, ?, ?, ?, ?)"""
                    params = (batchId, starttime.strftime('%Y-%m-%d %H:%M:%S'), endtime.strftime('%Y-%m-%d %H:%M:%S'), participants, title, mid, filepath)
                    cur.execute(query, params)
                    lastsessionid = cur.lastrowid
                    print("Session data inserted with SessionId:", lastsessionid)

                    attendancecreatequery = """insert into portal_studentattendance (StudentId,SessionId,JoinTime,LeaveTime,Duration)
                    select portal_student.studentid  , {sessionid} , temp_attendance_sheet.jointime , temp_attendance_sheet.leavetime , temp_attendance_sheet.duration
                     from temp_attendance_sheet join portal_student 
                    on temp_attendance_sheet.email = portal_student.StudentEmail""".format(sessionid=lastsessionid)
                    cur.execute(attendancecreatequery)
                    print("Attendance data inserted for SessionId:", lastsessionid)

                    try:
                        # Insert organizer details into portal_teacher_class_detail
                        cur.execute("""INSERT INTO portal_teacher_class_detail(Teacherintime,Teacherouttime,teacher_duration,Teacher_name,Teacheremail,UserID_id)
                                    SELECT
                                    temp_attendance_sheet.jointime,
                                    temp_attendance_sheet.leavetime,
                                    time(temp_attendance_sheet.duration, 'unixepoch') as duration,
                                    temp_attendance_sheet.fullname,
                                    temp_attendance_sheet.email,
                                    auth_user.id
                                    from temp_attendance_sheet JOIN auth_user on
                                    temp_attendance_sheet.role='Organizer'and lower(temp_attendance_sheet.email) = lower(auth_user.email)
                                    JOIN auth_user_groups on 
                                    auth_user_groups.user_id =auth_user.id where group_id=4""")
                        conn.commit()
                        print("Teacher/class details inserted.")
                    except:
                        pass

                    updatecoordinator = "update portal_session set sessioncoordinateuser = (select email from temp_attendance_sheet where role ='Organiser') where SessionId = {sessionid}".format(sessionid=lastsessionid)
                    cur.execute(updatecoordinator)
                    print("Coordinator updated for SessionId:", lastsessionid)

                    cur.execute("""select email from temp_attendance_sheet where temp_attendance_sheet.email in (
                                   select auth_user.email from auth_user join auth_user_groups on auth_user.id = auth_user_groups.user_id 
                                   join auth_group on auth_group.id = auth_user_groups.group_id
                                   and auth_group.name = 'Instructor')""")
                    res = cur.fetchall()

                    if res:
                        instructoremail = res[0][0]
                        if instructoremail:
                            cur.execute("Update portal_session set sessioninstructor = '{}'".format(instructoremail))
                            print("Instructor updated for SessionId:", lastsessionid)

                    conn.commit()

            except Exception as e:
                print("Error occurred:", e)
                pass

        conn.close()
        print("Connection closed.")

    # from django.db import IntegrityError

    # try:
    #     conn = sqlite3.connect('db.sqlite3')
    #     cur = conn.cursor()
        
    #     cur.execute("""INSERT INTO portal_teacher_class_detail(Teacherintime,Teacherouttime,teacher_duration,Teacher_name,Teacheremail,UserID_id)
    #                 SELECT
    #                 temp_attendance_sheet.jointime,
    #                 temp_attendance_sheet.leavetime,
    #                 time(temp_attendance_sheet.duration, 'unixepoch') as duration,
    #                 temp_attendance_sheet.fullname,
    #                 temp_attendance_sheet.email,
    #                 auth_user.id
    #                 from temp_attendance_sheet JOIN auth_user on
    #                 temp_attendance_sheet.role='Organizer'and lower(temp_attendance_sheet.email) = lower(auth_user.email)
    #                 JOIN auth_user_groups on 
    #                 auth_user_groups.user_id =auth_user.id where group_id=4""")
    #     conn.commit()
    #     print("Teacher/class details inserted.")
    # except IntegrityError as e:
    #     print("Integrity Error occurred:", e)
    #     pass

    print("Exiting upload_attendance_files function.")



