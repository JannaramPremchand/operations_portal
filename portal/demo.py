
from celery import shared_task
from django.http import JsonResponse
from pyrsistent import T
import requests
from django.shortcuts import render
import pandas as pd
from sqlalchemy import create_engine
from portal.models import assignment_data
from portal.graph_helper import *
from portal.auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_token,load_cache,save_cache,get_msal_app
from batch_portal.celery import app
import yaml
import msal
import os
import time
from . graph_helper import *
from django.contrib.auth.models import User


# from . import views


# @shared_task
# def add_csv_data():
#     file = 'data.csv'
#     df = pd.read_csv(file)
#     engine = create_engine('sqlite:///db.sqlite3')
#     # engine = create_engine(':memory:')
#     df1 = df.to_sql(demo._meta.db_table, if_exists='replace', con=engine, index=False)
#     print(demo._meta.db_table)
#     return df1

# @shared_task
# def delete_csv_data():
#     engine = create_engine('sqlite:///db.sqlite3')
#     conn = engine.connect()
#     trans = conn.begin()
#     conn.execute("DELETE from"+ " "+demo._meta.db_table)
#     trans.commit()
# #     # Close connection
#     conn.close()


@shared_task(bind=True)
def add_api_data(request,fun):
    import json
  #graph api base url
    base_url = "https://graph.microsoft.com/v1.0/"
    # endpoint = base_url +'education/me/assignments'
    # endpoint = base_url +'education/classes/9289f463-badc-4722-8b51-e6f1326a7f02/assignments'
    # endpoint = base_url +'education/classes/9289f463-badc-4722-8b51-e6f1326a7f02/members'
    # endpoint = base_url+ 'education/classes/9289f463-badc-4722-8b51-e6f1326a7f02/assignments/assignmentsid{{}}/submissions/submissionid{{}}/outcomes'
    
    headers = {'Authorization':'Bearer'}
    token = fun
    headers = {
        'Authorization': 'Bearer {0}'.format(token),
        'Content-Type': 'application/json'
    }

    # endpoint0 = base_url+ "education/classes/"
    # educatiom_data = json.loads(requests.get(endpoint0,headers=headers).text)


    # class_id = []
    # class_name = []
    # for i in range(len(educatiom_data['value'])):
    #     id_ = educatiom_data['value'][i]['id']
    #     name = educatiom_data['value'][i]['mailNickname']
    #     class_id.append(id_)
    #     class_name.append(name)

    class_id = ["9289f463-badc-4722-8b51-e6f1326a7f02"]
    class_name = ["MarchFullstack2021"]

    import pandas as pd

    myDataFrame = pd.DataFrame(columns = ['Id','Name','Email','Assingments','duedate','submiteddate','unsubmiteddate','returndate','reassingndate','status','feedback','points','assingment_delay','assingment_check_delay'])
    for class_data_id,class_data_name in zip(class_id,class_name):
        #assingment endpoint graph api url
        endpoint1 = base_url+ "education/classes/"+class_data_id+"/assignments/"
        #saving assingment id in list from assingment end point url 
        data = json.loads(requests.get(endpoint1,headers=headers).text)
        if data['value']:
            try:
                assingment_id = []
                for i in range(len(data['value'])):
                    assingment_id.append(data['value'][i]['id'])
            except KeyError as e:
                print(e)
        

        #creating muultiple assingment endpoint for grade url and saved into list
        
        outcomsurl = []
        for i in assingment_id:
        # endpoint2 = endpoint1 + i + "/submissions/?$filter=status"+" "+"eq"+" "+"'working'&?$expand=outcomes"
        # endpoint2 = endpoint1 + i + "/submissions/?$filter=status"+" "+"eq"+" "+"'submitted'&?$expand=outcomes"
        # endpoint2 = endpoint1 + i + '/susubmissions/?$filter=status eq "working"&?$expand=outcomes'
            endpoint2 = endpoint1 + i + "/submissions?$expand=outcomes"
            outcomsurl.append(endpoint2)

       
        #all student assingment json response
        
        data_upd_list = []
        for i in range(len(outcomsurl)):
            templist1 = []
            data2 = json.loads(requests.get(outcomsurl[i],headers=headers).text)
            value1 = data2['value']
            for j in value1:
                templist1.append(j)
            if '@odata.nextLink' in data2.keys():
                datalink = data2['@odata.nextLink']
                data_next = json.loads(requests.get(datalink,headers=headers).text)
                value2 = data_next['value']
                for k in value2:
                    templist1.append(k)
            data_upd_list.append(templist1)
        
        
        def multi_date(x):
            import pandas as pd
            final_date = []
            for i in range(len(data_upd_list)):
                date = []
                temp_id = []
                final_points1 = []
                final_points2 = []
                for j in range(len(data_upd_list[i])):
                    temp_id.append(data_upd_list[i][j]['submittedBy']['user']['id'])
                    if data_upd_list[i][j][x]==None:
                        date.append("Not Available")
                    else:
                        date.append(data_upd_list[i][j][x][:10])
                for id1,date1 in sorted(zip(temp_id,date),key = lambda x: x[0]):
                    zip_data = list((id1,date1))
                    final_points1.append(str(zip_data[0]))
                    final_points2.append(str(zip_data[1]))
                final_date.append(final_points1)
                final_date.append(final_points2)
            df = pd.DataFrame(final_date).T
            return df

        submit_df = multi_date('submittedDateTime')
        unsubmit_df = multi_date('unsubmittedDateTime')
        return_df = multi_date('returnedDateTime')
        reassingn_df = multi_date('reassignedDateTime')
        status_df = multi_date('status')

        def feedback():
            import pandas as pd
            final_feedback = []
            for i in range(len(data_upd_list)):
                feedback_text = []
                temp_id = []
                final_points1 = []
                final_points2 = []
                for j in range(len(data_upd_list[i])):
                    temp_id.append(data_upd_list[i][j]['submittedBy']['user']['id'])
                    if data_upd_list[i][j]['outcomes'][0]['publishedFeedback']==None:
                        feedback_text.append("No feedback")
                    else:
                        feedback_text.append(data_upd_list[i][j]['outcomes'][0]['publishedFeedback']['text']['content'])
                for id1,text in sorted(zip(temp_id,feedback_text),key = lambda x: x[0]):
                    zip_data = list((id1,text))
                    final_points1.append(zip_data[0])
                    final_points2.append(zip_data[1])
                final_feedback.append(final_points1)
                final_feedback.append(final_points2)
            df = pd.DataFrame(final_feedback).T
            return df

        feedback_df = feedback()


        
        assingment_data = []
        assingment_list = json.loads(requests.get(endpoint1,headers=headers).text)
        assingment_data.append(assingment_list)

        # #all user include teacher and student dispaly name ,email,id data
        member_endpoint = base_url+ "education/classes/"+class_data_id+ "/members?$select=id,displayName,userPrincipalName"
        teacher_endpoint = base_url+ "education/classes/"+class_data_id+ "/teachers?$select=id,displayName,userPrincipalName"
        member_data = []
        import pandas as pd
        member_list = json.loads(requests.get(member_endpoint,headers=headers).text)
        member_data.append(member_list)
        df_member = pd.DataFrame(member_data[0]['value'])

        # #Only teacher dispaly name ,email,id data
        teacher_data = []
        teacher_list = json.loads(requests.get(teacher_endpoint,headers=headers).text)
        teacher_data.append(teacher_list)
        df_teacher = pd.DataFrame(teacher_data[0]['value'])

        # #to get only student data we remove techer data into  all memeber this exclude teacher data and return only student data
        student_df = pd.concat([df_teacher,df_member], axis=0, ignore_index=True).drop_duplicates(subset=["id","userPrincipalName"],keep=False, ignore_index=True)
        student_df = student_df.sort_values(by='id').reset_index().drop('index',axis=1)
    
        # #this is final grade list of student sorted for by user id beacuse all assingment grade point mismatch with corrsopond users.
        final_points = []
        for i in range(len(data_upd_list)):
            temp_points = []
            temp_id = []
            final_points1 = []
            final_points2 = []
            for j in range(len(data_upd_list[i])):
                temp_id.append(data_upd_list[i][j]['submittedBy']['user']['id'])
                if (data_upd_list[i][j]['outcomes'][1]['points'] is None):
                    temp_points.append('No Points')
                else:
                    temp_points.append(str(data_upd_list[i][j]['outcomes'][1]['points']['points']))
            
            for letter, number in sorted(zip(temp_points,temp_id),key = lambda x: x[1]):
                zip_data = list((number,letter))
                final_points1.append(zip_data[0])
                final_points2.append(zip_data[1])
            final_points.append(final_points1)
            final_points.append(final_points2)

        # #assingment name saved into list used with name and id for pandas dataframe
        assignment_name1 = []
        for i in range(len(assingment_data[0]['value'])):
            var = assingment_data[0]['value'][i]['displayName']
            assignment_name1.append(var)

        assignment_duedate = []
        for i in range(len(data['value'])):
            var = data['value'][i]['dueDateTime'][:10]
            assignment_duedate.append(var)

        asdue_df = pd.DataFrame(assignment_duedate)
        asdue_df.columns = ['duedate']

        # #assingment name saved into list used for final dataframe
        assignment_name = []
        for i in range(len(assingment_data[0]['value'])):
            var = assingment_data[0]['value'][i]['displayName']
            assignment_name.append(var)

        #insert id column name with respective to assingment column
        for i in range(0,len(final_points),2):
            assignment_name.insert(i,f'id')
        
        df = pd.DataFrame(final_points).T
        df.columns = assignment_name

        new = []
        for i in range(0,len(df.columns),2):
            df1 = pd.merge(student_df,df.iloc[:, i:i+2],on='id',how='outer').iloc[:,-1].values.tolist()
            new.append(df1)

        # #final dataframe of student with grade of all student with respective to submitted assingment
        new_df = pd.DataFrame(new).T
        new_df.columns = assignment_name1
        final_df = pd.concat([student_df,new_df],axis=1)
        final_df = final_df.iloc[:student_df.shape[0],:final_df.shape[1]]
        final_df

        def column_name(id1,y):
            a = [id1,y]
            date = []
            for k in range(0,len(assignment_name1)):
                date.append(a[0])
                date.append(a[-1])
            return date


        def new_df(x,y):
            new1 = []
            for i in range(0,len(x.columns),2):
                df1 = pd.merge(y,x.iloc[:, i:i+2],on='id',how='outer').iloc[:,-1].values.tolist()
                new1.append(df1)
            new_df1 = pd.DataFrame(new1).T
            final_df1 = pd.concat([y,new_df1],axis=1)
            final_df1 = final_df1.iloc[:y.shape[0],:final_df1.shape[1]]
            return final_df1

        sdf = []
        submiteddate = column_name('id','submiteddate')
        submit_df.columns = submiteddate
        df1 = new_df(submit_df,student_df)
        sdf.append(df1)
        unsubmiteddate = column_name('id','unsubmiteddate')
        unsubmit_df.columns = unsubmiteddate
        df2 = new_df(unsubmit_df,student_df)
        sdf.append(df2)
        returndate = column_name('id','return')
        return_df.columns = returndate
        df3 = new_df(return_df,student_df)
        sdf.append(df3)
        reassingndate = column_name('id','reassingndate')
        reassingn_df.columns = reassingndate
        df4 = new_df(reassingn_df,student_df)
        sdf.append(df4)
        status = column_name('id','status')
        status_df.columns = status
        df5 = new_df(status_df,student_df)
        sdf.append(df5)
        feedback = column_name('id','feedback')
        feedback_df.columns = feedback
        df6 = new_df(feedback_df,student_df)
        sdf.append(df6)
        sdf.append(final_df)

        kd =[]
        kd1 =[]
        for i in range(0,final_df.shape[0]):
            md = []
            md1 = []
            for j in sdf:
                sd = j.iloc[i,3:].values.tolist()
                sdinfo = j.iloc[i,:3].values.tolist()
                md.append(sd)
                md1.append(sdinfo)
            kd.append(md)
            kd1.append(md1)

        

        from datetime import datetime
        assingnment_delay = []
        for i in range(final_df.shape[0]):
            f_delay= []
            for j in range(0,final_df.iloc[:,3:].shape[1]):
                s = asdue_df['duedate'][j]
                fs = pd.DataFrame((kd[i])).T
                fs.columns = ['submiteddate','unsubmiteddate','returndate','reassingndate','status','feedback','points']
                p = fs['submiteddate'][j]
                r = datetime.now().strftime("%Y-%m-%d")
                print(p)
                print(s)
                import numpy
                if type(p) is float or p =='Not Available' or p is None or type(p) is numpy.float64:
                    q = datetime.fromisoformat(r)-datetime.fromisoformat(s)
                    f_delay.append(q.days)
                else:
                    q = datetime.fromisoformat(p)-datetime.fromisoformat(s)
                    f_delay.append(q.days)
            assingnment_delay.append(f_delay)

        from datetime import datetime
        assingnment_check_delay = []
        for i in range(final_df.shape[0]):
            c_delay= []
            for j in range(0,final_df.iloc[:,3:].shape[1]):
                fs = pd.DataFrame((kd[i])).T
                fs.columns = ['submiteddate','unsubmiteddate','returndate','reassingndate','status','feedback','points']
                p = fs['submiteddate'][j]
                u = fs['feedback'][j]
                v = fs['points'][j]
                r = datetime.now().strftime("%Y-%m-%d")
                if ((type(u) is None or u =='No feedback') and (type(v) is None or v =='No Points')) and (p !='Not Available' or p is None):
                    c_data = datetime.fromisoformat(r)-datetime.fromisoformat(p)
                    # print(type(c_data))
                    c_delay.append(str(c_data.days))
                else:
                    c_delay.append('Not Available')
            assingnment_check_delay.append(c_delay)

        
        for i in range(0,final_df.shape[0]):
            fs = pd.DataFrame((kd[i])).T
            fs1 = pd.DataFrame(kd1[i][0]).T
            fs1.columns = ['Id','Name','Email']
            asgment = pd.DataFrame(assignment_name1)
            asgment.columns = ['Assingments']
            fs.columns = ['submiteddate','unsubmiteddate','returndate','reassingndate','status','feedback','points']
            assingment_delay_df = pd.DataFrame(assingnment_delay[i],columns =['assingment_delay'])
            assingment_check_delay = pd.DataFrame(assingnment_check_delay[i],columns =['assingment_check_delay'])
            newfs1 = pd.concat([fs1]*len(assignment_name1),ignore_index=True)
            newfs = pd.concat([newfs1,asgment,asdue_df,fs,assingment_delay_df,assingment_check_delay],axis=1)
            # print(newfs)
            myDataFrame = pd.concat([myDataFrame,newfs],axis=0,ignore_index=True)
    print(myDataFrame.shape)
    import pandas as pd
    table_name = 'portal_assignment_details'
    engine = create_engine('sqlite:///db.sqlite3')
    # Code to create a new temp table here.
    apidf = myDataFrame.to_sql(table_name, if_exists='replace', con=engine)

    # create cursor
    engine = create_engine('sqlite:///db.sqlite3')
    conn = engine.connect()
    trans = conn.begin()
    # QUery to backup the assignment details to history table, with timestamp
    # conn.execute('''INSERT OR IGNORE into portal_assignment_data 
    #     select   
    #     portal_student.StudentId , portal_batch.batchid,
    #     portal_assignment_details.Id as studenthash,
    #     portal_assignment_details.Assingments as assignments,
    #     portal_assignment_details.name,
    #     portal_assignment_details.Email,
    #     portal_assignment_details.duedate as duedate,
    #     portal_assignment_details.submiteddate as submiteddate,
    #     portal_assignment_details.unsubmiteddate as unsubmiteddate,
    #     portal_assignment_details.returndate as returndate,
    #     portal_assignment_details.reassingndate as reassingndate,
    #     portal_assignment_details.status as status,
    #     portal_assignment_details.feedback as feedback,
    #     portal_assignment_details.points as points,
    #     portal_assignment_details.assingment_delay as assingment_delay,
    #     portal_assignment_details.assingment_check_delay as assingment_check_delay

    #     from portal_assignment_details join portal_student 
    #     on name = portal_student.StudentName
    #     join portal_batch 
    #     on batchname =  portal_batch.BatchName''')
    

    conn.execute("Delete from portal_assignment_data")


    conn.execute('''INSERT into portal_assignment_data(studentapidata,Name,Email,assignments,duedate,submiteddate,unsubmiteddate,returndate,reassingndate,status,feedback,points,assingment_delay,assingment_check_delay,studentid_id,batchid_id)
        
        select
        portal_assignment_details.Id,   
        portal_assignment_details.name,
        portal_assignment_details.Email,
		portal_assignment_details.Assingments as assignments,
        portal_assignment_details.duedate as duedate,
        portal_assignment_details.submiteddate as submiteddate,
        portal_assignment_details.unsubmiteddate as unsubmiteddate,
        portal_assignment_details.returndate as returndate,
        portal_assignment_details.reassingndate as reassingndate,
        portal_assignment_details.status as status,
        portal_assignment_details.feedback as feedback,
        portal_assignment_details.points as points,
		portal_assignment_details.assingment_delay as assingment_delay,
        portal_assignment_details.assingment_check_delay as assingment_check_delay,
        
		portal_student.StudentId,
		portal_batchstudent.batchid
		


        from portal_assignment_details join portal_student 
        on portal_assignment_details.name = portal_student.StudentName
        join portal_batchstudent 
        on portal_batchstudent.StudentId =  portal_student.StudentId
		''')
    trans.commit()
    conn.close()
    # Query to insert data from assignment details temp to permanent table
    # cursor.execute("from portal_assignment_details join portal_student on name = portal_student.StudentName join portal_batch on batchname =  portal_batch.BatchName")
    return 

@shared_task
def delete_api_data():
    engine = create_engine('sqlite:///db.sqlite3')
    conn = engine.connect()
    trans = conn.begin()
    # table_name = 'assignment_details'
    conn.execute("DELETE from"+ " "+ assignment_data._meta.db_table)
    trans.commit()
    conn.close()

@shared_task(bind=True)
def add_meeting_attendence(request,fun):
#   meeting_data = task.add_meeting_attendence.delay(access_token(request))
  import json
#   graph api base url
  base_url = "https://graph.microsoft.com/v1.0/"
  endpoint = base_url +'me/events'
  headers = {'Authorization':'Bearer'}
  token = fun
#   print(token)
  headers = {
    'Authorization': 'Bearer {0}'.format(token),
    'Content-Type': 'application/json'
  }
  data = json.loads(requests.get(endpoint,headers=headers).text)
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
  import sqlite3
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
        import sqlite3
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

    return