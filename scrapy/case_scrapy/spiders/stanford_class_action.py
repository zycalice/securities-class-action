import scrapy
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
sys.path.append("..")
from case_scrapy.items import case_Items
from selenium.webdriver.support.ui import Select
from scrapy import Selector
import json
import re
import time
import datetime
import lxml.html as lh

class stanford_class_action(scrapy.Spider):
    name = "stanford_class_action"
    
    def start_requests(self):
        df_case_links_clean = pd.read_excel("/Users/yuchen.zhang/Documents/Projects/Class_Action/class_action_git/data/case_links_all.xlsx")
        case_links_clean = df_case_links_clean[0].tolist()
        for url in case_links_clean:
            yield scrapy.Request(url = url, callback = self.parse_pages)
                
    
    def parse_pages(self, response):
        case_soup = BeautifulSoup(response.text, 'lxml')
        c = case_Items()
        
        c['url'] = response.url

        
        # Basic Summary
        try:
            summary_section = case_soup.find(id = "summary")
            case_name = summary_section.find("div", attrs = {"class" : "page-header hidden-phone"}).text.strip().replace('Case Summary\n','')
            c["case_name"] = case_name
        except: pass
        
        
        # Case Summary
        try:
            case_section = case_soup.find(id = "summary")
            case_para = [x.text.strip() for x in case_section.find_all("div", attrs = {"class":"span12"})]
            c["case_brief"] = ''.join(case_para)
        

            case_status = case_section.find("p").getText().replace("\n","").replace("\xa0","").replace("\t","")
            case_status_list = [["Case Breif"] + case_para]
            for i, x in enumerate(case_status.split("  ")):
                x = x.strip()
                if x == "Case Status:":
                    c["case_status"] = case_status.split("  ")[1]
                else:
                    if x[:12] == "On or around":
                        c["date_of_last_review"] = x[13:(13+10)]
        except: pass
               
            
        # Plaintiff
        try:
            plaintiff_section = case_soup.find_all("ol", class_="styled")
            plaintiff = [x.text.strip() for x in plaintiff_section]
            plaintiff_list = plaintiff[0].split('\n\n\n')

            pstr = ""
            for x in plaintiff_list:
                if pstr == "":
                    pstr += x
                else:
                    pstr += ";" + x
            pstr

            c["plaintiffs"] = pstr
        except: pass
        
        
        # Company
        try:
            company_section = case_soup.find(id = "company")
            company = [x.text.strip() for x in company_section.find_all("div", attrs = {"class":"span4"})]

            for x in company:
                if len(x.split(": "))==2:
                    key,value = x.split(": ")
                else:
                    key,value = (x + " ").split(": ")
                key = '_'.join(key.split(" ")).lower()
                c[key] = value
        except: pass
        
            
        # fic (first identified complaint)
        try:
            fic_section = case_soup.find(id = "fic")
            fic = [x.text.strip() for x in fic_section.find_all("div", attrs = {"class":"span4"})]

            for x in fic:
                if len(x.split(": "))==2:
                    key,value = x.split(": ")
                else:
                    key,value = (x + " ").split(": ")
                key = re.sub('[^a-zA-Z0-9\n\.]', ' ',key).strip()
                key = '_'.join(key.split(" ")).lower()
                c[key] = value 
        except: pass
            
            
        # fic documents
        try:
            fic_documents = case_soup.find("table", {"class", "table table-bordered table-striped table-hover"})

            ## get titles
            fic_table_header = fic_documents.find('thead')
            fic_header = fic_documents.find_all('th')
            fic_header = [x.text.strip() for x in fic_header]
        except: pass
        
        ## get body
        try:
            fic_table_body = case_soup.find('tbody')
            fic_rows = fic_table_body.find_all('tr')
            fic_table_list = []
            for row in fic_rows:
                fic_cols=row.find_all('td')
                fic_cols=[x.text.strip() for x in fic_cols]
                fic_table_list.append(fic_cols)
        except: pass

        ## make a table
        try: 
            fic_summary_table = pd.DataFrame(fic_table_list)
            fic_summary_table.columns = fic_header
        except: pass
        
        
        # fic documents pdf links attach to table
        try:
            fic_links = fic_documents.find_all("tr", {"onclick" : re.compile("^window.location")})

            fic_links_list = []
            for x in fic_links:
                x = "http://securities.stanford.edu/" + x.get("onclick").replace("window.location=","").replace("'","")
                fic_links_list.append(x)

            fic_summary_table['link'] = pd.DataFrame(fic_links_list)
            c["fic_links_list"] = fic_links_list
            c["fic_summary_table"] = fic_summary_table.to_json()
        except: pass
        

        yield c
