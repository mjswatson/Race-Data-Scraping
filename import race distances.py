#get modules needed to run code
import requests
from datetime import *
import numpy as np
import csv
import time
#group to check for 
today=date.today()
group_used="Group 3"
#set up info needed to access website
url_base="https://www.racingpost.com"
payload = ""
headers = {
  'Cookie': 'RDSP=%7B%22rp_package%22%3A%22Unauthorized%22%7D; AccessToken=bb50afc0-c208-47cb-bb3d-0f8d29edf76d'
}
#chose dates to run between
start_date=date(2021,1,1)
date_final=date(2022,1,1)
#create save file name
#prepare variables to store data needed
races=[]
courses=[]
race_date=[]
race_length_m=[]
race_length_f=[]

date_use=start_date
#while date checked is less than final date
while date_use < date_final:
    #get the month in the correct form for the web address
    month_use=date_use.month
    if month_use<10:
        month_use="0"+str(month_use)
    else:
        month_use=str(month_use)
    #process day into correct form
    day_use=date_use.day
    if day_use<10:
        day_use="0"+str(day_use)
    else:
        day_use=str(day_use)

    #form the web address for the date
    url = "https://www.racingpost.com/results/"+str(date_use.year)+"-"+month_use+"-"+day_use
    #get the website information
    response = requests.request("GET", url, headers=headers, data=payload)

    web_text=response.text

    #check for any group races on that date
    group_count=web_text.count(group_used)
    'if there is a race from the group'
    if group_count>0:
        #get the names of every race from the correct group
        names=[]
        loc_start=0
        start_locations=[]
        for i in range(group_count):
            loc=web_text.find("("+group_used,loc_start)
            if loc>-1:
                start_loc=web_text.rfind("<span>",0,loc)
                end_loc=web_text.find("</span>",loc)
                names.append(web_text[start_loc+6:end_loc])
                start_locations.append(loc)
                loc_start=loc+1

        #only use unique race names for further analysis
        [use_names,idx]=np.unique(names,return_index=True)
        idx=idx.tolist()
        index=0
        #for each unique race get data
        for i in use_names:
            start=web_text.rfind("href=",0,start_locations[idx[index]])

            #record race date and name
            race_date.append(date_use)
            races.append(i)

            #get race URL and load race data
            end=web_text.find("\n",start)
            url_race=web_text[start+6:end-1]
            split_url=url_race.split("/")

            #get course name
            courses.append(split_url[3])

            length_start=web_text.find('text-race-distance',start)
            course_name_real_start=web_text.find('">',length_start)
            course_length_end=web_text.find('</span>',course_name_real_start)

            length=web_text[course_name_real_start+2:course_length_end]

            mile_check=length.find('m')
            furlough_check=length.find('f')

            if mile_check>-1:
                race_length_m.append(length[0:mile_check])
                if furlough_check>-1:
                    race_length_f.append(length[mile_check+1:furlough_check])
                else:
                    race_length_f.append(0)

            else:
                race_length_m.append(0)
                race_length_f.append(length[0:furlough_check])

    #go to the next day once all valid races processed
    file_name=group_used+" "+str(start_date)+"-"+str(date_use)+" distances.csv"
    date_use=date_use+timedelta(days=1)
    #print data analysed so progress can be monitored
    print(date_use)

#write data into rows for CSV
#write data titles
fields=['Race Name','Race Date','Course','Length (miles)','Length (f)']
rows=[]
#write data for each race into row format
for i in range(len(races)):
    rows.append([races[i],race_date[i],courses[i],race_length_m[i],race_length_f[i]])
#write csv file
with open(file_name, 'w') as f:
      
    # using csv.writer method from CSV package
    write = csv.writer(f)
    # write all data to file
    write.writerow(fields)
    write.writerows(rows)

    f.close()