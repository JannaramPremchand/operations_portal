import datetime

def createbatchanalytics():

    import sqlite3

    conn = sqlite3.connect(r'../db.sqlite3')

    cur = conn.cursor()

    cur.execute("""create table if not exists portal_batchanalytics (batchid number,studentcount number, activestudentcount number, droppedstudentcount number, laggingstudentcount number,
                    avg_attendance_last_5_sessions float, avg_availabilty_last_5_sessions float,
                    min_attendance_last_5_sessions float,max_attendance_last_5_sessions float,
                    avg_attendance_last_10_sessions float, avg_availabilty_last_10_sessions float)""")

    cur.execute("""insert into portal_batchanalytics select batchid , null, null, null, null, null, null,null,null,null,null from portal_batch
where batchid not in (select batchid from portal_batchanalytics ) """)
    

    conn.commit()

    cur.close()
    conn.close()

def etl():
    import sqlite3

    conn = sqlite3.connect(r'../db.sqlite3')

    cur = conn.cursor()

    cur.execute('select batchid from portal_batch')

    all_batches = cur.fetchall()

    for batch in all_batches :
        batchid = batch[0]
        print('BtachId ',batchid)


        

        cur.execute("""select coalesce(round(avg(studentdetails.studentattendancepercent)),0) ,coalesce(round(avg(studentdetails.studentavailabilitypercent)),0) from (
                        select
                        StudentID,StudentName,
                        StudentEmail,Status,
                        totalsessions,
                        studentsessions,
                        sessionminutes,
                        studentminutes,
                        (studentsessions*100/totalsessions) studentattendancepercent,
                        (studentminutes*100/sessionminutes) studentavailabilitypercent,
                        1 as SessionId,
                        BatchId
                        from
                        (
                        select portal_student.StudentId , portal_student.StudentName , portal_student.StudentEmail,portal_batchstudent.Status,
                        portal_batchstudent.BatchId,
                        (select count(*) from portal_session where sessionid in
                        (select sessionid from portal_session where portal_session.BatchId = {p_batchid} order by sessionid desc limit 5)) as totalsessions,
                        count(distinct studentattendance.sessionid) as studentsessions,
                        (select sum((strftime('%s',SessionEndDate) - strftime('%s',SessionStartDate))/60) from portal_session
                        where sessionid in
                        (select sessionid from portal_session where portal_session.BatchId = {p_batchid} order by sessionid desc limit 5)
                        ) sessionminutes,
                        sum(studentattendance.duration)/60 as studentminutes
                        from portal_batchstudent join portal_student
                        on portal_batchstudent.StudentId = portal_student.StudentId
                        LEFT OUTER JOIN
                        (select portal_studentattendance.duration ,portal_session.BatchId , portal_studentattendance.studentid, portal_session.SessionId
                        from portal_session JOIN portal_studentattendance
                        on portal_session.SessionId = portal_studentattendance.SessionId
                        where portal_session.sessionid in
                        (select sessionid from portal_session where portal_session.BatchId = {p_batchid} order by sessionid desc limit 5)) studentattendance
                        on studentattendance.BatchId = portal_batchstudent.BatchId
                        and studentattendance.studentid = portal_batchstudent.studentid
                        where portal_batchstudent.BatchId = {p_batchid}
                        group by portal_student.StudentName , portal_student.StudentEmail
                        ) student_details_main) studentdetails
                        where studentdetails.Status like 'Active%'
                        """.format(p_batchid=batchid))
        



        resultset =  cur.fetchall()

        print (resultset)
       
        avgattendance = resultset[0][0]
        avgavailability = resultset[0][1]

        cur.execute("select count(*) from portal_batchstudent where batchid = {p_batchid} ".format(p_batchid=batchid))
        allstudents =  cur.fetchall()[0][0]

        print('All Students ',allstudents)

        cur.execute("select count(*) from portal_batchstudent where batchid = {p_batchid} and  Status like 'Active%'".format(p_batchid=batchid))
        activestudents =  cur.fetchall()[0][0]

        cur.execute("select count(*) from portal_batchstudent where batchid = {p_batchid} and  lower(Status) like '%lagging%'".format(p_batchid=batchid))
        laggingstudents =  cur.fetchall()[0][0]

        



        print ('*******************Data Loading started for batchid {} at {}**************************\n'.format(batchid,str(datetime.datetime.now())))
    


        print ("""update portal_batchanalytics set studentcount = {p_allstudents}, activestudentcount = {p_activestudents},
                        laggingstudentcount = {p_laggingstudents} , avg_attendance_last_5_sessions = {p_avgattendance} , avg_availabilty_last_5_sessions = {p_avgavailability}
                        where batchid = {p_batchid}""".format(p_allstudents = allstudents,p_activestudents=activestudents,p_laggingstudents=laggingstudents
                                                              ,p_avgattendance=avgattendance,p_avgavailability=avgavailability,p_batchid=batchid))

        cur.execute("""update portal_batchanalytics set studentcount = {p_allstudents}, activestudentcount = {p_activestudents},
                        laggingstudentcount = {p_laggingstudents} , avg_attendance_last_5_sessions = {p_avgattendance} , avg_availabilty_last_5_sessions = {p_avgavailability}
                        where batchid = {p_batchid}""".format(p_allstudents = allstudents,p_activestudents=activestudents,p_laggingstudents=laggingstudents
                                                              ,p_avgattendance=avgattendance,p_avgavailability=avgavailability,p_batchid=batchid))

        print ('*******************Data Loading started for batchid {} at {}**************************\n'.format(batchid,str(datetime.datetime.now())))

        conn.commit()
        
                    
    cur.close()
    conn.close()

createbatchanalytics()
print('Initial Loading done\n')
etl()
print('Incremental Loading done\n')
    
