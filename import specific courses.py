#get modules needed to run code
import requests
from datetime import *
import numpy as np
import csv
import time
#group to check for 
today=date.today()
courses_check=open('List of Racecourses.txt').readlines()
#set up info needed to access website
url_base="https://www.racingpost.com"
payload = ""
headers = {
  'Cookie': 'RDSP=%7B%22rp_package%22%3A%22Unauthorized%22%7D; AccessToken=bb50afc0-c208-47cb-bb3d-0f8d29edf76d'
}
#chose dates to run between
start_date=date(2021,9,20)
date_final=date(2022,1,1)
#create save file name
#prepare variables to store data needed
races=[]
courses=[]
race_date=[]
win_distance=[]
no_female=[]
no_male=[]
ratio=[]
winner_gender=[]
second_gender=[]
win_weight_st_all=[]
win_weight_lb_all=[]
sec_weight_st_all=[]
sec_weight_lb_all=[]
win_age=[]
sec_age=[]

courses_use=[]
for i in courses_check:
    name=i.strip('\n')
    if name!='':
        courses_use.append(name.upper())

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
    days_courses=[]
    total_count=0
    #check for any group races on that date
    for i in courses_use:
        course_count=web_text.count(i)
        if course_count>0:
            days_courses.append(i)  
        total_count=course_count+total_count

    'if there is a race from the group'
    if total_count>0:
        for i in days_courses:
            #get the names of every race from the correct group
            search_text='coursename="'+i
            course_count=web_text.count(search_text)
            names=[]
            loc_start=0
            start_locations=[]
            for j in range(course_count):
                loc=web_text.find(search_text,loc_start)
                if loc>-1:
                    start_loc=web_text.find('="link-listCourseNameLink">\n                       <span>',loc)
                    abandoned_check=web_text.find('raceAbandoned">Abandoned',loc)
                    end_loc=web_text.find("</span>",start_loc)
                    no_link_check=web_text.find('raceCourse__panel__race__info__title__link">\n',loc)
                    if (end_loc<abandoned_check or abandoned_check==-1) and (no_link_check>end_loc or no_link_check==-1):
                        names.append(web_text[start_loc+len('="link-listCourseNameLink">\n                       <span>'):end_loc])
                        start_locations.append(loc)
                    elif no_link_check<end_loc and no_link_check>-1:
                        end_loc=web_text.find("                    </span>\n",no_link_check)
                        names.append(web_text[no_link_check+len('raceCourse__panel__race__info__title__link">\n                        '):end_loc])
                        start_locations.append(loc)

                    loc_start=loc+1

            #only use unique race names for further analysis
            [use_names,idx]=np.unique(names,return_index=True)
            idx=idx.tolist()
            index=0
            #for each unique race get data
            for j in use_names:
                start_use=start_locations[idx[index]]
                start=web_text.find('href="',start_use)
                if start<2000+start_use:
                #record race date and name
                    race_date.append(date_use)
                    races.append(j)
                    
                    #get race URL and load race data
                    end=web_text.find("\n",start)
                    url_race=web_text[start+6:end-1]
                    check_race=url_race.find('winning-times')
                    if check_race<0:
                        url_use=url_base+url_race
                        response = requests.request("GET", url_use, headers=headers, data=payload)
                        race_text=response.text
                        #check site hasnt had an error - if it has wait 5 mins and try again
                        error_check=race_text.find('Sorry, we\'re currently experiencing issues')
                        if error_check==-1:
                            #get course name
                            course_name_start=race_text.find('data-analytics-coursename="',0)
                            course_name_end=race_text.find('"\n',course_name_start)
                            courses.append(race_text[course_name_start+27:course_name_end])
                            #extract number of racers
                            no_racers=race_text.count("horseTable__pos__length")

                            #find data about the winner and second place
                            winner_loc=race_text.find("horseTable__pos__length")
                            second_loc=race_text.find("horseTable__pos__length",winner_loc+1)

                            #extract win distance
                            if no_racers>1:
                                win_dist_start=race_text.find("<span>",second_loc)
                                win_dist_end=race_text.find("</span>",win_dist_start)
                                win_dist=race_text[win_dist_start+6:win_dist_end]
                                win_distance.append(win_dist)
                            else:
                                win_distance.append([])

                            #get weight for win and second
                            #get stone value for winner
                            win_weight_st_start=race_text.find("horse-weight-st",0)
                            win_weight_st_end=race_text.find("<!--\n",win_weight_st_start)
                            win_weight_st=race_text[win_weight_st_end-2:win_weight_st_end]
                            #extract all numeric values - has to be done due to variable length of weight value
                            win_weight_st = [int(i) for i in win_weight_st if i.isdigit()]
                            win_weight_lb_f=""
                            for k in win_weight_st:
                                win_weight_st_f=win_weight_lb_f+str(k)
                            #get lb value for winner
                            win_weight_lb_start=race_text.find('horse-weight-lb"><!--\n',0)
                            win_weight_lb_end=race_text.find("<!--\n",win_weight_lb_start+len('horse-weight-lb"><!--\n'))
                            win_weight_lb=race_text[win_weight_lb_end-2:win_weight_lb_end]
                            win_weight_lb = [int(i) for i in win_weight_lb if i.isdigit()]
                            #extract all numeric values - has to be done due to variable length of weight value
                            for k in win_weight_lb:
                                win_weight_lb_f=win_weight_lb_f+str(k)
                            win_weight_st_all.append(float(win_weight_st_f))
                            if len(win_weight_lb_f)>0:
                                win_weight_lb_all.append(float(win_weight_lb_f))
                            else:
                                win_weight_lb_all.append(0)


                            #get st value for second
                            if no_racers>1:
                                sec_weight_st_start=race_text.find("horse-weight-st",win_weight_st_start+1)
                                sec_weight_st_end=race_text.find("<!--\n",sec_weight_st_start)
                                sec_weight_st=race_text[sec_weight_st_end-2:sec_weight_st_end]
                                sec_weight_st = [int(i) for i in sec_weight_st if i.isdigit()]
                                sec_weight_st_f=""
                                for k in sec_weight_st:
                                    sec_weight_st_f=sec_weight_st_f+str(k)
                                sec_weight_st_all.append(float(sec_weight_st_f))

                                #get lb value for second
                                sec_weight_lb_start=race_text.find('horse-weight-lb"><!--\n',win_weight_lb_start+1)
                                sec_weight_lb_end=race_text.find("<!--\n",sec_weight_lb_start+len('horse-weight-lb"><!--\n'))
                                sec_weight_lb=race_text[sec_weight_lb_end-2:sec_weight_lb_end]
                                sec_weight_lb = [int(i) for i in sec_weight_lb if i.isdigit()]
                                sec_weight_lb_f=""
                                for k in sec_weight_lb:
                                    sec_weight_lb_f=sec_weight_lb_f+str(k)

                                if len(sec_weight_lb_f)>0:
                                    sec_weight_lb_all.append(float(sec_weight_lb_f))
                                else:
                                    sec_weight_lb_all.append(0)
                            else:
                                sec_weight_st_all.append([])
                                sec_weight_lb_all.append([])

                            #get age for winner and second
                            win_age_start=race_text.find("horse-age",0)
                            win_age_end=race_text.find("<!--\n",win_age_start)
                            win_age_txt=race_text[win_age_end-1:win_age_end]
                            if win_age_txt==' ' or win_age_txt=='':
                                win_age.append([])
                            else:
                                win_age.append(float(win_age_txt))

                            if no_racers>1:
                                second_age_start=race_text.find("horse-age",win_age_start+1)
                                sec_age_end=race_text.find("<!--\n",second_age_start)
                                sec_age_txt=race_text[sec_age_end-1:sec_age_end]
                                if sec_age_txt==' ' or win_age_txt=='':
                                    sec_age.append([])
                                else:
                                    sec_age.append(float(sec_age_txt))
                            else:
                                sec_age.append([])


                            #extract gender of each racer
                            pos_loc=0
                            sexs=[]
                            #for each racer
                            for k in range(no_racers):
                                #find horse data
                                pos_loc=race_text.find("horseTable__pos__length",pos_loc+1)
                                #find horse profile url
                                profile_start=race_text.find("/profile/horse/",pos_loc)
                                profile_end=race_text.find("\n",profile_start)
                                profile_url=race_text[profile_start:profile_end-1]
                                horse_url=url_base+profile_url
                                #get horse profile webpage data
                                response = requests.request("GET", horse_url, headers=headers, data=payload)
                                horse_prof=response.text
                                #find data on horse sex
                                sex_start=horse_prof.find('"horseSex":')
                                sex_end=horse_prof.find('",',sex_start)
                                #extract horse sex
                                sex=horse_prof[sex_start+12:sex_end]
                                #process sex into male or female
                                if sex=="filly" or sex=="mare":
                                    sexs.append("female")
                                else:
                                    sexs.append("male")
                            #combine race sex data into overall values
                            females=sexs.count("female")
                            no_female.append(females)
                            males=sexs.count("male")
                            no_male.append(males)
                            if males==0:
                                ratio.append(1)
                            else:
                                ratio.append(females/males)

                            #record winners and seconds sex
                            winner_gender.append(sexs[0])
                            if no_racers>1:
                                second_gender.append(sexs[1])
                            else:
                                second_gender.append([])

                            #go to the next viable race on that day
                            index=index+1
                        else:
                            print('Error encountered, pausing and retrying')
                            time.sleep(120)
                    else:
                        courses.append(i.capitalize())
                        winner_gender.append([])
                        win_distance.append([])
                        win_weight_st_all.append([])
                        win_weight_lb_all.append([])
                        win_age.append([])
                        second_gender.append([])
                        sec_weight_st_all.append([])
                        sec_weight_lb_all.append([])
                        sec_age.append([])
                        no_male.append([])
                        no_female.append([])
                        ratio.append([])

    #go to the next day once all valid races processed
    file_name='all races'+" "+str(start_date)+"-"+str(date_use)+".csv"
    date_use=date_use+timedelta(days=1)
    #print data analysed so progress can be monitored
    print(date_use)

#write data into rows for CSV
#write data titles
fields=['Race Name','Race Date','Course','Winner Sex','Win Distance','Winner weight st','Winner weight lb','Winner Age','Second Sex','Second weight st','Second weight lb','Second Age','Number Males','Number Females','Ratio']
rows=[]
#write data for each race into row format
for i in range(len(races)):
    rows.append([races[i],race_date[i],courses[i],winner_gender[i],win_distance[i],win_weight_st_all[i],win_weight_lb_all[i],win_age[i],second_gender[i],sec_weight_st_all[i],sec_weight_lb_all[i],sec_age[i],no_male[i],no_female[i],ratio[i]])
#write csv file
with open(file_name, 'w') as f:
      
    # using csv.writer method from CSV package
    write = csv.writer(f)
    # write all data to file
    write.writerow(fields)
    write.writerows(rows)

    f.close()