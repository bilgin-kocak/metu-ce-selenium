# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 20:47:49 2021

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
import time   

def getQ(string, journal_name):
    if "Q1" in string:
        return "Q1"
    elif "Q2" in string:
        return "Q2"
    elif "Q3" in string:
        return "Q3"
    elif "Q4" in string:
        return "Q4"
    else:
        print("No Quartile: " + journal_name)
        return ""

path = os.getcwd() +"/"
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--incognito")
prefs = {"download.default_directory" : path}
options.add_experimental_option("prefs",prefs)
# options.add_argument("--headless")
driver = webdriver.Chrome(path+ "chromedriver.exe",options=options)
data = {}

timeout = 10
#driver.get("https://jcr.clarivate.com/JCRLandingPageAction.action?wsid=F1snOnpZx4TR3AOVrJD&Init=Yes&SrcApp=IC2LS&SID=H1-IPVgjLJkXb9JHHIdJbkbM3aLlcHlOjfy-18x2d6W6ty080uCRTPTpUU0DGKQx3Dx3D0g1DpIKVlQUPB8hzdx2Bkmvgx3Dx3D-03Ff2gF3hTJGBPDScD1wSwx3Dx3D-cLUx2FoETAVeN3rTSMreq46gx3Dx3D")

journals = pd.read_excel(path+"journal_list.xlsx",header=None, names=["Journal Name"])
errors = []

for i,row in journals.iterrows():
    driver.get("https://jcr.clarivate.com/JCRLandingPageAction.action?wsid=F1snOnpZx4TR3AOVrJD&Init=Yes&SrcApp=IC2LS&SID=H1-IPVgjLJkXb9JHHIdJbkbM3aLlcHlOjfy-18x2d6W6ty080uCRTPTpUU0DGKQx3Dx3D0g1DpIKVlQUPB8hzdx2Bkmvgx3Dx3D-03Ff2gF3hTJGBPDScD1wSwx3Dx3D-cLUx2FoETAVeN3rTSMreq46gx3Dx3D")
    journal_name = row["Journal Name"]
#    journal_name = journals.iloc[0,0]
    data[journal_name] = {}
    
    main_window = driver.window_handles[0]
    driver.implicitly_wait(5)
    
    input_el = driver.find_element_by_xpath("//input[@id='search-inputEl']")
    input_el.clear()
    input_el.send_keys(journal_name)
#    element = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='x-list-plain']/li")))
    try:
        elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='x-list-plain']/li")))
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//ul[@class='x-list-plain']/li[1]/a")))
    except:
        print("error on: "+journal_name)
        errors.append(journal_name)
        continue
#        driver.quit()
    
    element.click()
#    time.sleep(2)
    
#    link = driver.find_element_by_xpath("//ul[@class='x-list-plain']/li[1]/a")
#    link.click()
#    input_el.send_keys(Keys.RETURN)
#    time.sleep(3)
#    WebDriverWait(driver, 20).until(EC.new_window_is_opened(main_window))
    WebDriverWait(driver, 20).until(EC.number_of_windows_to_be(2))
#    WebDriverWait(driver,10).until(EC.frame_to_be_available_and_switch_to_it(driver.window_handles[1]))
    driver.switch_to_window(driver.window_handles[1])
#    driver.implicitly_wait(5)
#    driver.switch_to_window(driver.window_handles[1])
#    driver.implicitly_wait(5)
    # journal_categories = driver.find_element_by_xpath("//div[@class='journal-info-categories']/div[@class='category-array']")
    
    tabset = driver.find_elements_by_xpath("//div[@class='tabset journal-data-tabset cur-tab-1']/div[@class='tabset-head']/div")
    if len(tabset)==0:
        tabset = driver.find_elements_by_xpath("//div[@class='tabset cur-tab-1 journal-data-tabset']/div[@class='tabset-head']/div")
    for tab in tabset:
        if tab.text == "Rank":
#            print(tab.text)
            tab.click()
    
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tab-3']")))
    except:
        print("error2")
        driver.quit()
    
    rank_tab = driver.find_element_by_xpath("//div[@class='tabset-body jcr-table-tab']/div[@class='tab-3']")
    if rank_tab.text == "":
        rank_tab = driver.find_element_by_xpath("//div[@class='tabset-body']/div[@class='tab-3']")
    driver.implicitly_wait(5)
    rank = rank_tab.find_element_by_xpath(".//div[@class='component-body']/div[@class='rank']")
    driver.implicitly_wait(5)
    
    rows = rank_tab.find_elements_by_xpath(".//div[@class='component-body']/div[@class='rank']/div/div/div/div/div/div[@class='c']/div[@class='tb']/table/tbody/tr")
    # Bu özellik şimdilik kalsın
    # table_head = rank.find_element_by_xpath(".//div[@class='c']/div[@class='th scroll']/table")
            
    # table = rank.find_element_by_xpath(".//div[@class='c']/div[@class='tb']/table")
    # rows = table.find_elements_by_xpath("./tbody/tr")
    # table.get_attribute('innerHTML')
    # soup=BeautifulSoup(table.get_attribute('innerHTML'),'html.parser')
    # df_table=pd.read_html(str(soup))
    
    
    for row in rows:
        data[journal_name][row.text.split("\n")[0]] = getQ(row.text, journal_name)
    
    driver.close()
    driver.switch_to_window(main_window)

df = pd.DataFrame.from_dict(data)

df.to_excel(path+"result.xlsx")
# driver.quit()
# driver.switch_to_window(main_window)
