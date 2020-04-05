import read_rules as rr
import regex_generator as rg
import regex_end_finder as ref

import requests
import re
import time
import bs4
import json
from urllib.parse import urlsplit

__requires__ = ["requests==2.2.1"]
import pkg_resources

class learner:
    def __init__(self, filename = 'rule.json', page_count = 5):
        'Learner setup'
        self.ro = rr.rules(filename)
        #frontier: list of unvisited URLs, dictionary is an appropriate variable for searching
        self.frontier = dict.fromkeys(self.ro.get_seeds() , 1)
        self.visited = {}        
        self.web_site = self.ro.get_web_site()
        #start crawling
        url, v = self.frontier.popitem() # first record from frontier
        self.visited[url] = v #add url: k to the visited dictionary
        self.project_name = self.ro.get_project_name()
        self.filename = filename      
        self.result_file = self.ro.get_result_file()
        self.type = self.ro.get_type()
        self.wait = self.ro.get_wait()
        self.start = 0
        self.page_count = page_count
        if self.type == 'learner' != -1:
            self.download_scrap(url)            
        else:
            pass
    
    def download_scrap(self, url):
        'download url, create regex, learn regex, compare regex'
        html = self.download(url)
        if html != '':
            theRuleset, i = self.find_appropriate_ruleset(html, url)
            self.result = {} #refresh for new results
            if theRuleset != None: #rules are ready for scraping
                dataExraction_list = self.ro.get_sm_data_extraction(theRuleset)
                if len(dataExraction_list) > 0:
                    self.extracts_data(dataExraction_list, html, i) # data scraping 
                    print(self.start + 1, ":", url)
                    self.start += 1                   

                linkExtraction_list = self.ro.get_sm_link_extraction(theRuleset)
                if len(linkExtraction_list) > 0:
                    self.extracts_link(linkExtraction_list, html, i)
                
                

                #waiting list                
            if len(self.frontier) > 0: #if no links, process is finished
                k, v = self.frontier.popitem() #pop from frontier
                self.visited[k] = v
                if self.page_count > self.start:                    
                    self.download_scrap(k) #recursive
                else: #dump json results
                    temp = self.filename[:self.filename.find(".")]
                    with open(temp + "_new.json", 'w') as json_file:
                        json.dump(self.ro.data, json_file, indent=3, separators=(',', ': '), ensure_ascii=False)


    def extracts_data(self, dataExraction_list, html, i):
        'Data scraping from a web page'
        j = 0
        for theDataExtraction in dataExraction_list:
            parent_layout = self.ro.get_sm_parent_layout(theDataExtraction)
            extraction_rules = self.ro.get_sm_extraction_rules(theDataExtraction)            
            if parent_layout == '*':
                k = 0
                for theRule in extraction_rules:
                    result_type = self.ro.get_sm_extraction_result_type(theRule)                   
                    rule = self.ro.get_sm_extraction_rule_selector(theRule, result_type)
                    check_res, preferred_regex, _ = self.check_regex(rule, html, result_type)
                    if check_res:
                        try:
                            temp_key = self.ro.data["sitemap"][i]["data_extraction"][j]["extraction_rules"][k]["selector_regex"]
                            if temp_key != preferred_regex:
                                self.ro.data["sitemap"][i]["data_extraction"][j]["extraction_rules"][k]["selector_regex"] = 'Error'
                        except KeyError:
                            self.ro.data["sitemap"][i]["data_extraction"][j]["extraction_rules"][k]["selector_regex"] = preferred_regex                    
                    k += 1
            else:
                check_res, preferred_regex, part_html = self.check_regex(parent_layout, html, "innerHTML")
                if check_res:
                    try:
                        temp_key = self.ro.data["sitemap"][i]["data_extraction"][j]["parent_layout_regex"]
                        if temp_key != preferred_regex:
                            self.ro.data["sitemap"][i]["data_extraction"][j]["parent_layout_regex"] = 'Error'
                    except KeyError:
                        self.ro.data["sitemap"][i]["data_extraction"][j]["parent_layout_regex"] = preferred_regex
                k = 0
                for theRule in extraction_rules:
                    result_type = self.ro.get_sm_extraction_result_type(theRule)                   
                    rule = self.ro.get_sm_extraction_rule_selector(theRule, result_type)
                    check_res, preferred_regex, _ = self.check_regex(rule, part_html, result_type)
                    if check_res:
                        try:
                            temp_key = self.ro.data["sitemap"][i]["data_extraction"][j]["extraction_rules"][k]["selector_regex"]
                            if temp_key != preferred_regex:
                                self.ro.data["sitemap"][i]["data_extraction"][j]["extraction_rules"][k]["selector_regex"] = 'Error'
                        except KeyError:
                            self.ro.data["sitemap"][i]["data_extraction"][j]["extraction_rules"][k]["selector_regex"] = preferred_regex
                    k += 1
            j += 1        
        return
        
    def download(self, url):
        'Download a web page'
        res = ''
        try:
            if self.wait != 0:
                time.sleep(self.wait)
                res = requests.get(url)
        except:
            time.sleep(5) #wait 5 seconds
            res = requests.get(url)
        
        if res != '':
            res = res.text 

        return res

    def find_appropriate_ruleset(self, html, url):
        'sitemap detection: return a ruleset in json format'
        self.sitemap_page = ''
        i = 0 #for position data in sitemap, need for dump 
        for smp in self.ro.get_sitemap():
            c_key = 'url'
            c_value = self.ro.get_sm_detection(smp).get('url', '') #url is the prefered case
            if c_value == '':
                c_key = 'page'
                c_value = self.ro.get_sm_detection(smp).get('page', '')
                if c_value == '': #still empty, unexpected case
                    continue

            if c_key == 'url' and c_value == '=' and self.web_site == url: #the most of web pages don't contain additional information in url
                return smp, i
            else:
                if c_key == 'url':
                    if url.find(c_value) != -1:
                        return smp, i
                elif c_key == 'url':
                    if html.find(c_value) != -1:
                        return smp, i
            i += 1
        return None, -1

    def extracts_link(self, linkExraction_list, html, i):
        j = 0
        for theLinkExtraction in linkExraction_list:
            parent_layout = self.ro.get_sm_parent_layout(theLinkExtraction)
            extraction_rule = self.ro.get_sm_link_selector(theLinkExtraction)
            
            if parent_layout != '*':                
                check_res, preferred_regex, part_html = self.check_regex(parent_layout, html, "innerHTML")
                if check_res:
                    self.ro.data["sitemap"][i]["link_extraction"][j]["parent_layout_regex"] = preferred_regex
                
                link_pattern = rg.ahreftoRegex(extraction_rule)
                l = self.extract_link(link_pattern, part_html) 
                if len(l) > 0:
                    new_links = list(set(l)) #set eliminate duplicate record
                    self.add_web_site_information_to_url(new_links)  
            else:
                link_pattern = rg.ahreftoRegex(extraction_rule)
                l = self.extract_link(link_pattern, html) 
                if len(l) > 0:
                    new_links = list(set(l)) #set eliminate duplicate record
                    self.add_web_site_information_to_url(new_links) 
            j += 1 

        return

    def extract_link(self, rule, html):
        if self.type == 'learner': 
            return re.findall(rule, html, re.DOTALL)

    def add_web_site_information_to_url(self, new_links):
        for ind in range(len(new_links)):
            if new_links[ind] != None and len(new_links[ind]):
                if not (new_links[ind].startswith("http:") or new_links[ind].startswith("https:") or new_links[ind].startswith("//")): #add http and web site name to link, (/.../..../) -> http://website/.../..../
                    if new_links[ind].startswith("/"):
                        base_url = "{0.scheme}://{0.netloc}".format(urlsplit(self.web_site))
                        new_links[ind] = base_url + new_links[ind]
                    else:
                        if new_links[ind].startswith("/"):
                            new_links[ind] = self.web_site + new_links[ind][1:]
                        else:
                            new_links[ind] = self.web_site + new_links[ind]

                        
                if new_links[ind].startswith("//"):
                    temp_ind = new_links[ind].index("/", 2)
                    new_links[ind] = self.web_site + new_links[ind][temp_ind+1:]
                #add record to frontier
                if new_links[ind] not in self.frontier and new_links[ind] not in self.visited: #to prevent duplicate links
                    self.frontier[new_links[ind]] = 1
        return

    def check_regex(self, rule, html, result_type):
        tag_pattern = rg.csstoRegex(rule, "HTMLtag") #css to regex, only tag
        if result_type == "HTMLtag":
            return True, tag_pattern, ""
        else:
            res_rg = re.search(tag_pattern, html, re.DOTALL) #search pattern in html
            if res_rg != None:
                res_rg = res_rg.group() #only tag
                endp, data_result = ref.find_uniqueEndPattern(res_rg, html)                
                preferred_regex = tag_pattern + "(.*?)" + endp
                #generator_regex = rg.csstoRegex(rule) #innerHTML
                preferred_regex = ''.join([i if ord(i) < 128 else '.' for i in preferred_regex])
                return True, preferred_regex, data_result
            else:
                return False, "", ""                
    