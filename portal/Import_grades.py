#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import re
import sqlite3


conn = sqlite3.connect('db.sqlite3' , check_same_thread=False)
# In[77]:


# Importing the grades file from Microsoft Teams


# In[4]:

# import_grades function will import the files to create grade records. Use TEAMS or REPL as category


def import_grades_from_repl(filename):
    repldf = pd.read_csv(filename)
    targetdf =  pd.DataFrame(columns = ['Name' , 'Email','percentfinish','AssignmentName' , 'AssignmentProperty' , 'AssignmentValue'])
    columnvals = list()



    for i in range(len(repldf)) :
        
        # Defining all the column values variables here
        name = ''
        email = ''
        percent_finish =''
        assignment_name = ''
        assignment_property = ''
        assignment_value = ''
        listproperties = [re.compile('(.+)(Status$)') , re.compile('(.+)(Timestamp$)') ,re.compile('(.+)(Unit Tests Passed\s+\([0-9]+\)$)')]
        
        
        columnvals =  list(zip(repldf.columns,repldf.iloc[i]))
        #print (columnvals)
        #print (len(columnvals))
        for j in range(len(columnvals)):
            if columnvals[j][0] =='Name':
                name =  str(columnvals[j][1])
            elif columnvals[j][0] =='Email':
                email =  columnvals[j][1]
            elif columnvals[j][0] =='Percent Complete':
                percent_finish =  columnvals[j][1]
            else:
                for pattern in listproperties :
                    search = re.search(pattern , columnvals[j][0] )
                    if search:
                        assignment_name =  search.group(1)
                        assignment_property =  search.group(2)
                        assignment_value = columnvals[j][1]
                        interimdf =  {'Name' : name , 'Email' : email ,
                                  'percentfinish' : percent_finish ,'AssignmentName' : assignment_name,
                                  'AssignmentProperty' : assignment_property, 'AssignmentValue' : str(assignment_value)}
                        targetdf = targetdf.append(interimdf, ignore_index = True)                
    targetdf.to_sql('portal_studentwork' , if_exists='append', con=conn , index=False, method= None )    


def import_grades_from_team(filename):
    teamdf = pd.read_csv(filename )
    targetdf =  pd.DataFrame(columns = ['Name' , 'Email','percentfinish','AssignmentName' , 'AssignmentProperty' , 'AssignmentValue'])
    columnvals = list()


    for i in range(len(teamdf)) :
        
        # Defining all the column values variables here
        name = ''
        email = ''
        percent_finish =''
        assignment_name = ''
        assignment_property = ''
        assignment_value = ''
        
        columnvals =  list(zip(teamdf.columns,teamdf.iloc[i]))
        #print (columnvals)
        #print (len(columnvals))
        for j in range(len(columnvals)):
            if columnvals[j][0] =='First Name':
                name = name + str(columnvals[j][1])
            elif columnvals[j][0] =='Last Name':
                name = name + str(columnvals[j][1])
            elif columnvals[j][0] =='Email Address':
                email =  columnvals[j][1]
            else:
                if  'Points' not in columnvals[j][0]  and 'Feedback' not in  columnvals[j][0] :
                    assignment_name = columnvals[j][0]
                    
                    #Multiple dataframe insert commands for all the properties which are part of the assignment.
                   
                
                    """
                    Copy the below sections for every property value combo
                    """
                    assignment_property = 'Points' # Property name for points
                    assignment_value = columnvals[j+1][1] #Property value for points
                    #print (name,email,assignment_name,assignment_property,assignment_value)
                    
                    interimdf =  {'Name' : name , 'Email' : email ,
                                  'percentfinish' : percent_finish ,'AssignmentName' : assignment_name,
                                  'AssignmentProperty' : assignment_property, 'AssignmentValue' : str(assignment_value)}
                    
                    targetdf = targetdf.append(interimdf, ignore_index = True)                
                    
                    """
                    Copy the above sections for every property value combo
                    """
                    
                    """
                    Copy the below sections for every property value combo
                    """
                    
                    assignment_property = 'Feedback' # Property name for Feedback
                    assignment_value = columnvals[j+2][1] #Property value for Feedback 
                    #print (name,email,assignment_name,assignment_property,assignment_value)
                    
                    interimdf =  {'Name' : name , 'Email' : email ,
                                  'percentfinish' : percent_finish ,'AssignmentName' : assignment_name,
                                  'AssignmentProperty' : assignment_property, 'AssignmentValue' : str(assignment_value)}
                    
                    targetdf = targetdf.append(interimdf, ignore_index = True)  
                    """
                    Copy the above sections for every property value combo
                    """
    targetdf.to_sql('portal_studentwork' , if_exists='append', con=conn , index=False, method= None )

    




def import_grades(filename, category):
    conn = sqlite3.connect('db.sqlite3' , check_same_thread=False)
    if category == 'TEAMS' :
        import_grades_from_team(filename)
    elif category == 'REPL' :
        import_grades_from_repl(filename)
    else:
        raise Exception("Wrong Category Defined")
    conn.close()




