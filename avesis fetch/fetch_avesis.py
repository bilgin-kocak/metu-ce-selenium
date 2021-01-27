# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 22:25:25 2021

@author: kocak
"""
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException      


pathForChromeDriver = "C:\\Users\\kocak\\Downloads\\chromedriver.exe"
path = os.getcwd() +"\\"
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--incognito")
prefs = {"download.default_directory" : path}
options.add_experimental_option("prefs",prefs)
# options.add_argument("--headless")
driver = webdriver.Chrome(pathForChromeDriver,options=options)

def get_year(description, user_code):
    years = list(range(1975,2023))
    desc_year = []
    for year in years:
        if str(year) in description:
            desc_year.append(str(year))
    if len(desc_year) > 1:
        print(f"More than one year are found: {user_code}")
        print(f"Years: {desc_year}")
    if not desc_year:
        year = ""
    else:
        year = desc_year[-1]
    return year

timeout = 10
driver.get("https://ce.metu.edu.tr/en/faculty-members")
driver.implicitly_wait(5)
# try:
#     WebDriverWait(driver, timeout).until(EC.visibility_of_all_elements_located() ((By.XPATH, "//div[@class='person']")))

# finally:
#     print("Timed out waiting for page to load: https://ce.metu.edu.tr/en/faculty-members")
#     driver.quit()

person_els = driver.find_elements_by_xpath("//div[@class='person']")
old_webpages = []
faculty_members = {}
for person_el in person_els:
    user_code = person_el.text.split("\n")[-2].split("{at}")[0].strip().lower()
    user_name = person_el.text.split("\n")[-4]
    faculty_members[user_name] = user_code

faculty_members["Cem Topkaya"] = "ctopkaya"

for user_name in faculty_members.keys():
    user_code = faculty_members[user_name]
    publication_link = f"https://avesis.metu.edu.tr/{user_code}/yayinlar"
    driver.get(publication_link)
    driver.implicitly_wait(2)
    
    try:
        #identify element
        l = driver.find_element_by_xpath("//div[@class='pubs-wrapper']")
        #NoSuchElementException thrown if not present
    except NoSuchElementException:
        print(f"Old Webpage for {user_name}")
        old_webpages.append(user_name)
        continue
    # try:
    #     WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='pubs-wrapper']")))
    # finally:
    #     print("Timed out waiting for page to load: " + user_name)
    #     driver.quit()
    
    
    xpath = "//h4[@class='with-underline']"
    groups = driver.find_elements_by_xpath(xpath)
    group_names = [group.text for group in groups] 
    
    xpath = "//div[@class='pubs-wrapper']"
    all_data = driver.find_elements_by_xpath(xpath)
    paper_titles = []
    paper_authors = []
    paper_descriptions = []
    for element in all_data:
        title_elements = element.find_elements_by_xpath(".//h3[@class='title']")
        paper_titles.append([title_element.text for title_element in title_elements])
        
        descript_els = element.find_elements_by_xpath(".//div[@class='description']")
        paper_authors.append([descript_el.text.split("\n")[0] for descript_el in descript_els])
        paper_descriptions.append([descript_el.text.split("\n")[1] for descript_el in descript_els])
    
    if len(group_names) != len(paper_authors):
        print(f'Enterasan {user_code}')
    
    types = []    
    authors = []
    titles = []
    descriptions = []
    for i in range(len(group_names)):
        authors = authors + paper_authors[i]
        types = types + [group_names[i]]*len(paper_authors[i])
        titles += paper_titles[i]
        descriptions += paper_descriptions[i] 
    person = [user_name]*len(types)
    
    info_dict = {"Faculty Member":person,
                 "Authors": authors,
                 "Title": titles,
                 "Type": types,
                 "Description": descriptions,}
    
    df = pd.DataFrame.from_dict(info_dict)
    temp_desc = df.loc[0,"Description"]
    temp_desc.split(",")
    df["Year"] = df["Description"].apply(lambda x: get_year(x, user_code))
    
    directory = path + 'faculty members paper infos avesis'
    if not os.path.exists(directory):
        os.makedirs(directory)
    df.to_excel(directory + "\\" + user_name +  ".xlsx")
    
for user_name in old_webpages:
    user_code = faculty_members[user_name]
    publication_link = f"https://avesis.metu.edu.tr/{user_code}/yayinlar"
    driver.get(publication_link)
    driver.implicitly_wait(2)
    
    try:
        #identify element
        l = driver.find_element_by_xpath("//div[@class='row cv-section']")
        #NoSuchElementException thrown if not present
    except NoSuchElementException:
        print(f"No paper for {user_name}")
        old_webpages.append(user_name)
        continue
    
    row_els = driver.find_elements_by_xpath("//div[@class='row cv-section']")
    years = []
    types = []
    titles = []
    authors = []
    descriptions = []
    for row_el in row_els:
        try: 
            row_title = row_el.find_element_by_xpath(".//div[@class='cv-section-title']")
        except NoSuchElementException:
            continue
        if row_title.text == "SCI, SSCI ve AHCI İndekslerine Giren Dergilerde Yayınlanan Makaleler":
            items = row_el.find_elements_by_xpath(".//div[@class='cv-item']")
            for item in items:
                years.append(item.text.split("\n")[0])
                titles.append(item.text.split("\n")[1])
                authors.append(item.text.split("\n")[2])
                descriptions.append(item.text.split("\n")[3])
            types += [row_title.text]*len(items)
        elif row_title.text == "Diğer Dergilerde Yayınlanan Makaleler":
            items = row_el.find_elements_by_xpath(".//div[@class='cv-item']")
            for item in items:
                years.append(item.text.split("\n")[0])
                titles.append(item.text.split("\n")[1])
                authors.append(item.text.split("\n")[2])
                descriptions.append(item.text.split("\n")[3])
            types += [row_title.text]*len(items)
        elif row_title.text == "Hakemli Kongre / Sempozyum Bildiri Kitaplarında Yer Alan Yayınlar":
            items = row_el.find_elements_by_xpath(".//div[@class='cv-item']")
            for item in items:
                years.append(item.text.split("\n")[0])
                titles.append(item.text.split("\n")[1])
                authors.append(item.text.split("\n")[2])
                descriptions.append(item.text.split("\n")[3])
            types += [row_title.text]*len(items)
    
    person = [user_name]*len(types)
    
    info_dict = {"Faculty Member":person,
                 "Authors": authors,
                 "Title": titles,
                 "Type": types,
                 "Description": descriptions,}
    
    df = pd.DataFrame.from_dict(info_dict)
    temp_desc = df.loc[0,"Description"]
    temp_desc.split(",")
    df["Year"] = df["Description"].apply(lambda x: get_year(x, user_code))
    
    directory = path + 'faculty members paper infos avesis'
    if not os.path.exists(directory):
        os.makedirs(directory)
    df.to_excel(directory + "\\" + user_name +  ".xlsx")

driver.quit()

#%%
directory = path + 'faculty members paper infos avesis'
files = [file[2] for file in os.walk(directory)][0]
df_combined = pd.read_excel(directory+"\\"+files[0])
for i in range(1,len(files)):
    df_temp = pd.read_excel(directory+"\\"+files[i])
    df_combined = df_combined.append(df_temp, ignore_index=True)
    
df_combined.to_excel(directory+ "\\faculty_member_combined_paper_infos_avesis.xlsx" )