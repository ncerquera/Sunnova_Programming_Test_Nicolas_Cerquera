#!/usr/bin/env python
# coding: utf-8

# In[1]:


#loading libraries
import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt # this is used for the distance function on part 3.f.


# In[2]:


#Importing data from excel file, Data, and Monthly Expected Production (MEP) as data frames
xls = pd.ExcelFile('Sample_Data_Programming_Test_07062020.xlsx')


# ###  a.Read the Data and Monthly Expected Production sheets, each into its own separate DataFrame

# In[3]:


Data = pd.read_excel(xls,'Data', index=0)
MEP = pd.read_excel(xls,'Monthly Expected Production')


# In[4]:


Data.info()


# ### b. Remove any systems with duplicate serial numbers 

# In[5]:


# I will be creating multiple independent copies (deep copying) to avoid shallow copying for each of the tasks

dfb = Data.copy()
dfb = dfb.drop_duplicates(['Meter Serial Number'], keep = 'first')
dfb.info()


# ### c. Correct the System Size so that any system less than 2.0 kW is set to 2.0 kW

# In[6]:


dfc = dfb.copy()

dfc['System Size (kW) Corrected'] = [2 if x < 2 else x for x in dfc['System Size (kW)']] #create a new column with the condition of system size< 2 = 2
dfc.info()


# ### d. Set any negative daily production values to 0.0 (each of the days represents a production in kWh)
# 

# In[7]:


dfd = dfc.copy()

dfd.info()
dfd.head()


# In[8]:


col_list = dfd.columns # creating a list with the columns of dfd data frame
col_list


# In[9]:


non_date_cols =['System ID','Meter Serial Number','In-Service Date','PTO Date','Contract Type','Installation State','System Size (kW)','Latitude','Longitude','System Size (kW) Corrected']


# In[10]:


date_cols = set(col_list) - set(non_date_cols)
date_cols= list(date_cols) # creating a list of columns that have the shared characteristic of being a date
dfd[date_cols]= dfd[date_cols].mask(dfd[date_cols]<0,0) # in the date columns, select the negative values(boolean) and use a mask to replace them with 0


# In[11]:


(dfd[date_cols]<0).any().any() # confirm there are no negative values in the daily production values


# In[12]:


dfd


# ### e. For each system, fill in the missing daily production values according to this: Use the Monthly Expected Production from that tab divided by the number of days in that month as the fill in value for days missing in that  month.
# 
# 

# In[13]:


#e.For each system, fill in the missing daily production values according to this: Use the Monthly Expected Production from that tab divided by the number of days in that month as the fill in value for days missing in that  month.
MEP.info()


# In[14]:


MEP['Days']= MEP['Month'].dt.days_in_month  # create a new column with the number of days in the month based on Month
MEP['Fill in Values (kWh)'] = MEP['Monthly Expected Production']/MEP['Days'] 
MEP


# In[15]:


MEP['Month_Number'] = MEP['Month'].apply(lambda m : m.month ) # create the month number for having column values


# In[16]:


MEP.loc[MEP['Month_Number']==7,'Fill in Values (kWh)'].values[0]


# In[17]:


date_cols[0]


# In[18]:


Mgroup = MEP.groupby(["Month_Number"])


# In[19]:


dfe = dfd.copy() 
dfe[date_cols].isnull().sum() # provide the number of null values on each day ( multiple systems in a day can have a null value)


# In[20]:


dfe.index


# In[21]:


date_cols[0].month


# In[22]:


dfe = dfe.reset_index(drop = True)  # index values reset to account for missign values in the index (tricky)


# In[23]:


# We are selecting the values that are nan in the list of columns
for k in date_cols:
    for i,j in enumerate(dfe[k]):  # gives the approriate index and value of the element of the column K
        if np.isnan(j):   # if there is a 'nan' in element j
            print('hello') # just for testing
            print(dfe.loc[i,k]) # before applying the selection
            dfe.loc[i,k] = MEP.loc[MEP['Month_Number']==k.month,'Fill in Values (kWh)'].values[0] 
            print(dfe.loc[i,k]) #after


# In[24]:


dfe[date_cols].isnull().sum() # confirm there are no elements who have not been assigned a value


# ### f. Find the distance for all systems from Houston Hobby Airport, which is located at 29.644866, -95.276985 - find the closest system to Hobby Airport and print out the System ID and how far the system is from Hobby airport in miles. You may use/copy a reference function if you need to for this section.
# 
# 

# In[25]:


dff = dfe.copy()


# In[26]:


Hobby_Airport = [29.644866, -95.276985]


# In[27]:


def transferdistance(lon1, lat1, lon2, lat2):  
    """ Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)    """
    # convert decimal degrees to radians     
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2]) 
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 
    return c * r


# Reference: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

# In[28]:


transferdistance(Hobby_Airport[1],Hobby_Airport[0],dff['Longitude'][0],dff['Latitude'][0]) #checking the function works correctly


# In[29]:


dff['Distance from Hobby'] = dff.apply(lambda x : transferdistance(Hobby_Airport[1],Hobby_Airport[0],x['Longitude'],x['Latitude']),
                                       axis=1) 
#create a new column that captures the result of applying the fuction to each pair of Longitude and Latitude columns


# In[30]:


dff # distances added as a column on the right hand side of the dff data frame


# In[31]:


dff['Distance from Hobby'].min() # closest system distance in miles


# In[32]:


dff[dff['Distance from Hobby'] == dff['Distance from Hobby'].min()]['System ID'].values[0]


# ### g. Calculate each systems monthly production, which will include changes made in previous steps

# In[33]:


dfg=dff.copy()


# In[34]:


M_cols=[k for k in date_cols if k.month==1] # list comprehension using a list(date_cols) to create a list(M_cols)


# In[35]:


Month_List=[] # initializa the list
for i in range(1,13): # created a for loop of 12 elements
    #print(i)
    Month_List.append(f'Month_{i}') # add a month as a string to name a column associated with i
    M_cols=[k for k in date_cols if k.month==i] # return k for k in date_cols if the month of k is equal to i
    dfg[f'Month_{i}']=dfg[M_cols].sum(axis=1)


# In[36]:


dfg


# ### h. Output a summary excel file named "Sunnova_Programming_Test_Excel_Output_FirstName_LastName", inserting your first and last name where appropriate, with the system ID, the system size, the distance from Hobby Airport, and the system monthly production.

# In[37]:


Month_List


# In[38]:


Subset = ['System ID','System Size (kW) Corrected','Distance from Hobby']
Subset


# In[39]:


Total_List = []
Total_List = Subset + Month_List
Total_List


# In[40]:


Export = dfg[Total_List]


# In[41]:


Export.to_excel("Sunnova_Programming_Test_Excel_Output_Nicolas_Cerquera.xlsx") 


# In[ ]:




