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
    name = "stanford_class_action_full"
    
    def start_requests(self):
        urls = ["http://securities.stanford.edu/filings.html?page=1"]
        for url in urls:
            yield scrapy.Request(url = url, callback = self.parse)
    
        df_case_links_clean = pd.read_excel("/Users/yuchen.zhang/Documents/Projects/Class_Action/class_action_git/data/case_links_all.xlsx")
        case_links_clean = df_case_links_clean[0].tolist()
        for url in case_links_clean:
            yield scrapy.Request(url = url, callback = self.parse)
    
    def parse(self,response):
        # Get raw links
        case_links = []
        i = 1
        first_page_html = requests.get("http://securities.stanford.edu/filings.html?page=1").text
        next_page_html = requests.get("http://securities.stanford.edu/filings.html?page=" + str(i+1)).text

        while first_page_html != next_page_html:
            try:
                driver.get("http://securities.stanford.edu/filings.html?page=" + str(i))
                sel_case = Selector(text=driver.page_source)
                case_links_raw = sel_case.css('tr:nth-child(n)::attr(onclick)').getall()
                case_links.append(case_links_raw)

                i += 1
                next_page_html = requests.get("http://securities.stanford.edu/filings.html?page=" + str(i)).text
            except: break
        
        # Change the links to actual links replacing the window.location part
        case_links_clean = []
        for i in range(0, len(case_links)):
            for j in range(0, len(case_links[i])):
                case_links_clean.append("http://securities.stanford.edu/" + case_links[i][j].replace("window.location=","").replace("'",""))


        # Perform Parse
        df_case_links_clean = pd.read_excel("/Users/yuchen.zhang/Documents/Projects/Class_Action/class_action_git/data/case_links_all.xlsx")
        case_links_clean = df_case_links_clean[0].tolist()
        
        for url in case_links_clean:
            yield response.follow(url = url, callback = self.parse_pages)
                
    
    def parse_pages(self, response):
        case_soup = BeautifulSoup(response.text, 'lxml')

        c = case_Items
        c['url'] = response.url

        # Basic Summary
        summary_section = case_soup.find(id = "summary")
        case_name = summary_section.find("div", attrs = {"class" : "page-header hidden-phone"}).text.strip().replace('Case Summary\n','')

        c["case_name"] = case_name
        
        
        # Case Summary
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
                    
        # Plaintiff
        plaintiff_section = case_soup.find_all("ol", class_="styled")
        plaintiff = [x.text.strip() for x in plaintiff_section]
        plaintiff_list = [["Plaintiffs",''.join(plaintiff[0].split("\n\n\n"))]]
        c["plaintiffs"] = str(plaintiff[0].split("\n\n\n"))
        
        # Company
        company_section = case_soup.find(id = "company")
        company = [x.text.strip() for x in company_section.find_all("div", attrs = {"class":"span4"})]

        for x in company:
            key,value = x.split(": ")
            key = '_'.join(key.split(" ")).lower()
            c[key] = value
            
        # fic (first identified complaint)
        fic_section = case_soup.find(id = "fic")
        fic = [x.text.strip() for x in fic_section.find_all("div", attrs = {"class":"span4"})]

        for x in fic:
            key,value = x.split(": ")
            key = re.sub('[^a-zA-Z0-9\n\.]', ' ',key).strip()
            key = '_'.join(key.split(" ")).lower()
            c[key] = value 
        
        # fic documents
        fic_documents = case_soup.find("table", {"class", "table table-bordered table-striped table-hover"})

        ## get titles
        fic_table_header = fic_documents.find('thead')
        fic_header = fic_documents.find_all('th')
        fic_header = [x.text.strip() for x in fic_header]

        ## get body
        fic_table_body = case_soup.find('tbody')
        fic_rows = fic_table_body.find_all('tr')
        fic_table_list = []
        for row in fic_rows:
            fic_cols=row.find_all('td')
            fic_cols=[x.text.strip() for x in fic_cols]
            fic_table_list.append(fic_cols)

        ## make a table
        fic_summary_table = pd.DataFrame(fic_table_list)
        fic_summary_table.columns = fic_header
        
        # fic documents pdf
        fic_links = fic_documents.find_all("tr", {"onclick" : re.compile("^window.location")})

        fic_links_list = []
        for x in fic_links:
            x = "http://securities.stanford.edu/" + x.get("onclick").replace("window.location=","").replace("'","")
            fic_links_list.append(x)

        c["fic_links_list"] = fic_links_list
        c["fic_summary_table"] = fic_summary_table
        c["fic_summary_table"]['link'] = pd.DataFrame(fic_links_list)
        

        yield c
