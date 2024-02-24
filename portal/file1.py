f = open(r'/home/ec2-user/portal/portal/myfile.sql')
import sqlite3
conn = sqlite3.connect('/home/ec2-user/portal/db.sqlite3')
curr = conn.cursor()
curr.execute("Delete from portal_assignment_data")


text = f.read()




inserts = text.split(';')



for insertsql in inserts :
    curr.execute(insertsql)



conn.commit()
conn.close()




#print (inserts[0])




#print (inserts[1])




#print (inserts[-1])
