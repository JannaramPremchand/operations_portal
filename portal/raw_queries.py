


StudentAttendanceSummaryQuery = """select
StudentID,StudentName,
StudentEmail,Status,
totalsessions,
studentsessions,
sessionminutes,
studentminutes,
(studentsessions*100/totalsessions)||'%' as studentattendancepercent,
(studentminutes*100/sessionminutes)||'%' as studentavailabilitypercent,
1 as SessionId,
BatchId
from
(
select portal_student.StudentId , portal_student.StudentName , portal_student.StudentEmail,portal_batchstudent.Status,
portal_batchstudent.BatchId,
(select count(*) from portal_session where portal_session.BatchId = {pk}) as totalsessions,
count(distinct studentattendance.sessionid) as studentsessions,
(select sum((strftime('%s',SessionEndDate) - strftime('%s',SessionStartDate))/60) from portal_session where portal_session.BatchId = {pk}
) sessionminutes,
sum(studentattendance.duration)/60 as studentminutes
from portal_batchstudent join portal_student
on portal_batchstudent.StudentId = portal_student.StudentId
LEFT OUTER JOIN
(select portal_studentattendance.duration ,portal_session.BatchId , portal_studentattendance.studentid, portal_session.SessionId
from portal_session JOIN portal_studentattendance
on portal_session.SessionId = portal_studentattendance.SessionId) studentattendance
on studentattendance.BatchId = portal_batchstudent.BatchId
and studentattendance.studentid = portal_batchstudent.studentid
where portal_batchstudent.BatchId = {pk}
group by portal_student.StudentName , portal_student.StudentEmail
) student_details_main
order by studentminutes DESC ;"""

StudentAttendanceSummaryQueryTop10 = """select
StudentID,StudentName,
StudentEmail,Status,
totalsessions,
studentsessions,
sessionminutes,
studentminutes,
(studentsessions*100/totalsessions)||'%' as studentattendancepercent,
(studentminutes*100/sessionminutes)||'%' as studentavailabilitypercent,
1 as SessionId,
BatchId
from
(
select portal_student.StudentId , portal_student.StudentName , portal_student.StudentEmail,portal_batchstudent.Status,
portal_batchstudent.BatchId,
(select count(*) from portal_session where portal_session.BatchId = {pk}) as totalsessions,
count(distinct studentattendance.sessionid) as studentsessions,
(select sum((strftime('%s',SessionEndDate) - strftime('%s',SessionStartDate))/60) from portal_session where portal_session.BatchId = {pk}
) sessionminutes,
sum(studentattendance.duration)/60 as studentminutes
from portal_batchstudent join portal_student
on portal_batchstudent.StudentId = portal_student.StudentId
LEFT OUTER JOIN
(select portal_studentattendance.duration ,portal_session.BatchId , portal_studentattendance.studentid, portal_session.SessionId
from portal_session JOIN portal_studentattendance
on portal_session.SessionId = portal_studentattendance.SessionId) studentattendance
on studentattendance.BatchId = portal_batchstudent.BatchId
and studentattendance.studentid = portal_batchstudent.studentid
where portal_batchstudent.BatchId = {pk}
group by portal_student.StudentName , portal_student.StudentEmail
) student_details_main
order by studentminutes DESC limit 10;"""

StudentHighestPlacement = """select
StudentID,StudentName,
StudentEmail,Status,
totalsessions,
studentsessions,
sessionminutes,
studentminutes,
(studentsessions*100/totalsessions)||'%' as studentattendancepercent,
(studentminutes*100/sessionminutes)||'%' as studentavailabilitypercent,
1 as SessionId,
BatchId
from
(
select portal_student.StudentId , portal_student.StudentName , portal_student.StudentEmail,portal_batchstudent.Status,
portal_batchstudent.BatchId,
(select count(*) from portal_session where portal_session.BatchId = {pk}) as totalsessions,
count(distinct studentattendance.sessionid) as studentsessions,
(select sum((strftime('%s',SessionEndDate) - strftime('%s',SessionStartDate))/60) from portal_session where portal_session.BatchId = {pk}
) sessionminutes,
sum(studentattendance.duration)/60 as studentminutes
from portal_batchstudent join portal_student
on portal_batchstudent.StudentId = portal_student.StudentId
LEFT OUTER JOIN
(select portal_studentattendance.duration ,portal_session.BatchId , portal_studentattendance.studentid, portal_session.SessionId
from portal_session JOIN portal_studentattendance
on portal_session.SessionId = portal_studentattendance.SessionId) studentattendance
on studentattendance.BatchId = portal_batchstudent.BatchId
and studentattendance.studentid = portal_batchstudent.studentid
where portal_batchstudent.BatchId = {pk}
group by portal_student.StudentName , portal_student.StudentEmail
) student_details_main
order by studentminutes DESC limit 15;"""

StudentLowestPlacement = """select
StudentID,StudentName,
StudentEmail,Status,
totalsessions,
studentsessions,
sessionminutes,
studentminutes,
(studentsessions*100/totalsessions)||'%' as studentattendancepercent,
(studentminutes*100/sessionminutes)||'%' as studentavailabilitypercent,
1 as SessionId,
BatchId
from
(
select portal_student.StudentId , portal_student.StudentName , portal_student.StudentEmail,portal_batchstudent.Status,
portal_batchstudent.BatchId,
(select count(*) from portal_session where portal_session.BatchId = {pk}) as totalsessions,
count(distinct studentattendance.sessionid) as studentsessions,
(select sum((strftime('%s',SessionEndDate) - strftime('%s',SessionStartDate))/60) from portal_session where portal_session.BatchId = {pk}
) sessionminutes,
sum(studentattendance.duration)/60 as studentminutes
from portal_batchstudent join portal_student
on portal_batchstudent.StudentId = portal_student.StudentId
LEFT OUTER JOIN
(select portal_studentattendance.duration ,portal_session.BatchId , portal_studentattendance.studentid, portal_session.SessionId
from portal_session JOIN portal_studentattendance
on portal_session.SessionId = portal_studentattendance.SessionId) studentattendance
on studentattendance.BatchId = portal_batchstudent.BatchId
and studentattendance.studentid = portal_batchstudent.studentid
where portal_batchstudent.BatchId = {pk}
group by portal_student.StudentName , portal_student.StudentEmail
) student_details_main
order by studentminutes ASC limit 15;"""


AllCoursesQuery = """SELECt portal_coursecategory.CourseCategoryId, portal_category.CategoryName , portal_course.CourseName , portal_course.CourseId as CRS
from portal_category join portal_coursecategory
on portal_category.CategoryId = portal_coursecategory.CategoryId
join portal_course on portal_course.CourseId = portal_coursecategory.CourseId
where portal_category.CategoryName like 'Full Stack%'
order by portal_coursecategory.CourseId asc"""

AllModulesQuery = """SELECT child.ModuleId, child.ModuleName,
child.ModuleType, child.SelfLearningLink,child.WorkLink,
parent.ModuleName as parentModuleName
from portal_course join portal_coursemodule child on portal_course.CourseId = child.CourseId
left outer join portal_coursemodule parent on child.ParentModuleId = parent.ModuleId
where portal_course.CourseId = {}"""

AssignmentQuery="""select * from (
select firstname , lastname , EmailAddress, round(avg(assignmentgrade),1) avg_assignment
from studentgrades
group by firstname , lastname , EmailAddress
)
order by avg_assignment DESC"""


StudentAttendanceSummaryQueryTop1 = """select
StudentID,StudentName,
StudentEmail,Status,
totalsessions,
studentsessions,
sessionminutes,
studentminutes,
(studentsessions*100/totalsessions)||'%' as studentattendancepercent,
(studentminutes*100/sessionminutes)||'%' as studentavailabilitypercent,
1 as SessionId,
BatchId
from
(
select portal_student.StudentId , portal_student.StudentName , portal_student.StudentEmail,portal_batchstudent.Status,
portal_batchstudent.BatchId,
(select count(*) from portal_session where portal_session.BatchId in {pk}) as totalsessions,
count(distinct studentattendance.sessionid) as studentsessions,
(select sum((strftime('%s',SessionEndDate) - strftime('%s',SessionStartDate))/60) from portal_session where portal_session.BatchId in {pk}
) sessionminutes,
sum(studentattendance.duration)/60 as studentminutes
from portal_batchstudent join portal_student
on portal_batchstudent.StudentId = portal_student.StudentId
LEFT OUTER JOIN
(select portal_studentattendance.duration ,portal_session.BatchId , portal_studentattendance.studentid, portal_session.SessionId
from portal_session JOIN portal_studentattendance
on portal_session.SessionId = portal_studentattendance.SessionId) studentattendance
on studentattendance.BatchId = portal_batchstudent.BatchId
and studentattendance.studentid = portal_batchstudent.studentid
where portal_batchstudent.BatchId in {pk} and portal_batchstudent.StudentId={sId}
group by portal_student.StudentName , portal_student.StudentEmail
) student_details_main
order by studentminutes DESC ;"""


StudentsGradesQuery = """select Name , 
Email , 
PercentFinish , 
AssignmentName , 
AssignmentProperty , 
AssignmentValue
from portal_studentwork
where Email in 
(select portal_student.StudentEmail
from portal_studentattendance join portal_student
on portal_studentattendance.StudentId = portal_student.StudentId
JOIN portal_session on portal_session.SessionId = portal_studentattendance.SessionId
where portal_session.BatchId = {}
group by portal_student.StudentName , portal_student.StudentEmail)"""


StudentAttendanceDetailsQuery="""Select StudentName,
BatchName,
sessiontitle,
SessionStartDate,
substr(jointime,  instr(jointime, ' ') + 1) AS JoinTime,
substr(leavetime,    instr(leavetime, ' ') + 1) AS LeaveTime
from portal_studentattendance Join portal_student on portal_student.StudentId = portal_studentattendance.StudentId
JOIN portal_session on portal_session.SessionId = portal_studentattendance.SessionId
JOIN portal_batch on portal_batch.BatchId = portal_session.BatchId
where portal_student.StudentId ={}
ORDER BY SessionStartDate DESC;"""


Total_Student_Count = """Select BatchId,
BatchName,
StatusName,
CategoryName,
studentcount,
avg_attendance_last_5_sessions,
avg_availabilty_last_5_sessions
FROM
(
SELECT portal_batch.BatchId,portal_batch.BatchName,portal_status.StatusName,portal_category.CategoryName,
(SELECT count(*) FROM portal_batchstudent WHERE portal_batchstudent.BatchId=portal_batch.BatchId AND portal_batchstudent.EndDate IS NULL 
AND portal_batchstudent.Status NOT LIKE 'dropped%') as studentcount,
portal_batchanalytics.avg_attendance_last_5_sessions,portal_batchanalytics.avg_availabilty_last_5_sessions
FROM portal_batch  JOIN portal_status on portal_batch.StatusId = portal_status.StatusId
join portal_category on portal_batch.CategoryId = portal_category.CategoryId
left OUTER join portal_batchanalytics on portal_batch.BatchId = portal_batchanalytics.batchid
)ORDER BY BatchId ASC;"""


BatchFiterByCategory="""Select BatchId,
BatchName,
StatusName,
CategoryName,
studentcount,
avg_attendance_last_5_sessions,
avg_availabilty_last_5_sessions
FROM
(
SELECT portal_batch.BatchId,portal_batch.BatchName,portal_status.StatusName,portal_category.CategoryName,
(SELECT count(*) FROM portal_batchstudent WHERE portal_batchstudent.BatchId=portal_batch.BatchId AND portal_batchstudent.EndDate IS NULL 
AND portal_batchstudent.Status NOT LIKE 'dropped%') as studentcount,
portal_batchanalytics.avg_attendance_last_5_sessions,portal_batchanalytics.avg_availabilty_last_5_sessions
FROM portal_batch  JOIN portal_status on portal_batch.StatusId = portal_status.StatusId
join portal_category on portal_batch.CategoryId = portal_category.CategoryId
left outer join portal_batchanalytics on portal_batch.BatchId = portal_batchanalytics.batchid

)WHERE CategoryName='{category}'
ORDER BY BatchId ASC;"""


AllStudents = """select StudentId,StudentName,StudentEmail ,BatchName,Status,StartDate,EndDate from 
(
select portal_student.StudentId,portal_student.StudentName,portal_student.StudentEmail,
portal_batchstudent.Status,portal_batch.BatchName,
portal_batchstudent.StartDate,portal_batchstudent.EndDate
from portal_batchstudent JOIN portal_batch on portal_batchstudent.BatchId = portal_batch.BatchId
JOIN portal_student on portal_batchstudent.StudentId = portal_student.StudentId
)ORDER BY StudentName ASC;"""


Teacher_attendance_lastweek = """SELECT 
 p.Teacher_Name , p.Teacherintime , p.Teacherouttime , p.teacher_duration,
(SUM(teacher_duration) over() /3600)||' hours  '||(SUM(teacher_duration) over() %60)||' minutes' as total_duration
from portal_teacher_class_detail p
WHERE  
(Teacherintime BETWEEN strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime', 'weekday 0', '-6 days')
AND strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'));"""

Teacher_attendance_lastmonth = """SELECT 
 p.Teacher_Name , p.Teacherintime , p.Teacherouttime , p.teacher_duration,
(SUM(teacher_duration) over() /3600)||' hours  '||(SUM(teacher_duration) over() %60)||' minutes' as total_duration
from portal_teacher_class_detail p
WHERE  
(Teacherintime BETWEEN strftime('%Y-%m-%d %H:%M:%S','now','start of month','0 month','0 day')
AND strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'));"""

# Teacher_attendance_lastweek = """SELECT * FROM portal_teacher_class_detail WHERE  (Teacherintime BETWEEN strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime', 'weekday 0', '-6 days') AND strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'));"""

# Teacher_attendance_lastmonth = """SELECT * FROM portal_teacher_class_detail WHERE  (Teacherintime BETWEEN strftime('%Y-%m-%d %H:%M:%S','now','start of month','0 month','0 day') AND strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'));"""

# Total_hr_min = """SELECT sum(teacher_duration),
#  (SUM(teacher_duration)/3600)||' hours  '||(SUM(teacher_duration)%60)||' minutes' FROM portal_teacher_class_detail;"""

AllTeacher = """SELECT DISTINCT	Teacher_name,Teacheremail,UserID_id FROM portal_teacher_class_detail;"""

operationuserforticket = """	
			select userdetails.id as id , (case when userdetails.id =1 then 'admin' else userdetails.fullname end) as fullname ,
		   	(case when userdetails.id =1 then 'admin@digikull.com' else userdetails.email end) as  email 
		    from 
			(SELECT auth_user.id , first_name||' '||last_name as fullname, auth_user.email from auth_user
                JOIN auth_user_groups on
                auth_user_groups.user_id =auth_user.id where group_id=1) userdetails join portal_tickets
				on portal_tickets.assignedtouser = userdetails.id
			   where ticketid = {ticketid}
				
			union all
			
			select userdetails.id , userdetails.fullname end ,userdetails.email END
		    from 
			(SELECT auth_user.id , first_name||' '||last_name as fullname, auth_user.email from auth_user
                JOIN auth_user_groups on
                auth_user_groups.user_id =auth_user.id where group_id=1 and auth_user.id <> 1) userdetails 
			    where userdetails.id not in
				(select assignedtouser from portal_tickets  where ticketid = {ticketid})"""

statusforticket = """SELECT portal_ticketstatus.ticketstatusid,portal_ticketstatus.ticketstatusname from portal_tickets join portal_ticketstatus
            on portal_tickets.ticketstatus = portal_ticketstatus.ticketstatusid where portal_tickets.ticketid ={ticketid}
            union all
            SELECT portal_ticketstatus.ticketstatusid,portal_ticketstatus.ticketstatusname from  portal_ticketstatus
            where portal_ticketstatus.ticketstatusid not in (select ticketstatus from portal_tickets 
            where portal_tickets.ticketid ={ticketid})"""