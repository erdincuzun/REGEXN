import read_rules as rr
import io_operation as ioo
import browser_interactions as bi
import time as t
import requests
import re
import time
import bs4
from urllib.parse import urlsplit

import memory_profiler
import os

def timeit(loop = 1, arg = 1):
    def timeit_sub(func):
        def timed(*args, **kw):
            ts = time.time()            
            m1 = memory_profiler.memory_usage()[0]
            result = func(*args, **kw)
            m2 = memory_profiler.memory_usage()[0]
            

            for _ in range(loop - 1):
                result = func(*args, **kw)
            te = time.time()

            arg1 = '-1'
            arg2 = '-1'
            if arg == 1:
                arg1 = args[1].replace('\n', '').replace('\r', '')
                arg2 = '-1'
                if len(args) > 2:
                    arg2 = args[2]

            #save log file
            project_path = os.getcwd() + "/" + args[0].project_name + "/"
            if not os.path.exists(project_path):    
                os.mkdir(project_path)
            if not os.path.exists(project_path + "log_" + args[0].type + ".csv"):
                with open(project_path + "log_" + args[0].type + ".csv", 'w') as f: 
                    f.write('ProjectName,FunctionName,Type,Parser,DiffMemory,DiffTime,Rule,lenHTML,lenRes\n') 
            else:
                my_list = [args[0].project_name, func.__name__.upper(),args[0].type,args[0].parser,(m2 - m1) * 1024, (te - ts) * 1000,  arg1, len(arg2), len(result)]
                my_string = ','.join([str(elem) for elem in my_list])
                with open(project_path + "log_" + args[0].type + ".csv", 'a') as f: 
                    f.write(my_string + '\n')
                    print(my_string)

            return result
        return timed
    return timeit_sub

class crawler:
    def __init__(self, filename='rule.json'):
        'Crawler setup'
        self.ro = rr.rules(filename)
        
        # frontier: list of unvisited URLs, dictionary is an appropriate variable for searching
        self.frontier = dict.fromkeys(self.ro.get_seeds(), 1)
        self.visited = {}
        self.web_site = self.ro.get_web_site()
        # start crawling
        url, v = self.frontier.popitem()  # first record from frontier
        self.visited[url] = v  # add url: k to the visited dictionary
        self.project_name = self.ro.get_project_name()
        self.ioo = ioo.io_operation(self.project_name)  # Create directory for a project
        self.filename = filename
        self.result_file = self.ro.get_result_file()
        self.type = self.ro.get_type()
        self.wait = self.ro.get_wait()
        self.browser = self.ro.get_browser()
        self.scroll_count=self.ro.get_scrollcount()

        self.driver = self.ro.get_driver()
        self.result = {}  # this variable is used to store data, extraction results in JSON format
        self.parser = 'regex' #default
        ## Selecting type:
        if self.type != "text-based":
            if self.type.find("dom") != -1:
                self.parser = self.type[self.type.find(':') + 1:]
                self.type = 'dom'
            elif self.type.find("selenium") != -1:
                self.parser = self.type[self.type.find(':') + 1:]
                self.type = 'selenium'
                self.br = bi.BrowserInteractions(url, self.browser, self.driver, self.wait, self.scroll_count)

        if self.type in ["text-based", "dom", "selenium"]:
            self.download_scrap(url)
            print(self.type)
        else:
            pass

    def download_scrap(self, url):
        'download url and scrap data'
        print(url)
        html = self.download(url)

        if html != '':
            if self.type == 'dom':
                self.ioo.save_html_file(str(html))  # save the web page
            elif self.type == "selenium":
                self.ioo.save_html_file(str(html))
            else:
                self.ioo.save_html_file(html)
            
            res = bs4.BeautifulSoup(str(html), "lxml")
            row = url + "," + str(len(str(html))) + "," + str(len(res.findAll())) 
            self.ioo.save_extraction_results([row], filename="weburl")

            theRuleset = self.find_appropriate_ruleset(html, url)
            self.result = {}  # refresh for new results
            if theRuleset != None:  # rules are ready for scraping
                dataExraction_list = self.ro.get_sm_data_extraction(theRuleset)
                if len(dataExraction_list) > 0:
                    self.extracts_data(dataExraction_list, html)  # data scraping
                    # save extraction results
                    self.ioo.save_extraction_results(self.ioo.preparedatatoSave(self.result), self.result_file)

                linkExtraction_list = self.ro.get_sm_link_extraction(theRuleset)
                if len(linkExtraction_list) > 0:
                    self.extracts_link(linkExtraction_list, html)
        
            # waiting list
        if len(self.visited) < 51:
                if len(self.frontier) > 0:  # if no links, process is finished
                    k, v = self.frontier.popitem()  # pop from frontier
                    self.visited[k] = v
                    self.download_scrap(k)

    def extracts_data(self, dataExraction_list, html):
        'Data scraping from a web page'
        for theDataExtraction in dataExraction_list:
            parent_layout = self.ro.get_sm_parent_layout(theDataExtraction)
            extraction_rules = self.ro.get_sm_extraction_rules(theDataExtraction)
            if parent_layout == '*':
                for theRule in extraction_rules:
                    rule_name = self.ro.get_sm_extraction_rule_name(theRule)
                    result_type = self.ro.get_sm_extraction_result_type(theRule)
                    # three kind of output as a result: innerHTML, outerHTML, HTMLtag
                    rule = self.ro.get_sm_extraction_rule_selector(theRule, result_type)
                    temp_data = self.extract_all_html(rule, html)
                    if not rule.startswith('img'):
                        temp_data = self.apply_filters(temp_data, theRule, result_type)
                    else:
                        #create dir, save url
                        temp_data = self.ioo.download_save_file(temp_data, self.web_site, self.type)

                    self.result[rule_name] = temp_data  # extraction rules
            else:
                part_htmls = self.extract_parent_layouts(parent_layout, html)
                for part_html in part_htmls:
                    for theRule in extraction_rules:
                        rule_name = self.ro.get_sm_extraction_rule_name(theRule)
                        result_type = self.ro.get_sm_extraction_result_type(theRule)
                        rule = self.ro.get_sm_extraction_rule_selector(theRule, result_type)
                        res_sub = self.extract_all_layout(rule, part_html)
                        res_sub = self.apply_filters(res_sub, theRule, result_type)
                        if rule_name in self.result:
                            self.result[rule_name] += res_sub  # like append mode
                        else:
                            self.result[rule_name] = res_sub  # means the first record of the rule_name
        return


    @timeit(loop = 250)
    def extract_all_html(self, rule, html):  # all extraction process new function for performance / time operations, in order to save time results.
        if self.type == 'text-based':
            return re.findall(rule, html, re.DOTALL)
        elif self.type == 'dom' or self.type == 'selenium':
            return html.select(rule)

    @timeit(loop = 250)
    def extract_parent_layouts(self, rule, html):
        if self.type == 'text-based':
            return re.findall(rule, html, re.DOTALL)
        elif self.type == 'dom' or self.type == 'selenium':
            return html.select(rule)

    @timeit(loop = 250)
    def extract_all_layout(self, rule, html):
        if self.type == 'text-based':
            return re.findall(rule, html, re.DOTALL)
        elif self.type == 'dom' or self.type == 'selenium':
            return html.select(rule)
    

    def download(self, url):
        'Download a web page'
        res = ''
        if self.type == "selenium":
            self.br.set_url(url)
            html = self.br.return_html()
            res = bs4.BeautifulSoup(html, self.parser)
        else:
            res = self.download_url(url)

            if self.type == 'dom':
                res = self.prepare_dom_or_text(res)
                
        return res
    
    @timeit(loop = 1, arg = 0)
    def prepare_dom_or_text(self, res):
        res = bs4.BeautifulSoup(res, self.parser)
        return res
    
    @timeit(loop = 1, arg = 0)
    def download_url(self, url):
        res = ''
        try:
            if self.wait != 0:
                time.sleep(self.wait)
                res = requests.get(url)
        except:
            time.sleep(5)  # wait 5 seconds and try again
            try:
                res = requests.get(url)
            except:
                res = ''
        if res != '':
            return res.text
        else:
            return ''
        
    def find_appropriate_ruleset(self, html, url):
        'sitemap detection: return a ruleset in json format'
        self.sitemap_page = ''
        for smp in self.ro.get_sitemap():
            c_key = 'url'
            c_value = self.ro.get_sm_detection(smp).get('url', '')  # url is the prefered case
            if c_value == '':
                c_key = 'page'
                c_value = self.ro.get_sm_detection(smp).get('page', '')
                if c_value == '':  # still empty, unexpected case
                    continue

            if c_key == 'url' and c_value == '=' and self.web_site == url:  # the most of web pages don't contain additional information in url
                return smp
            else:
                if c_key == 'url':
                    if url.find(c_value) != -1:
                        return smp
                elif c_key == 'url':
                    if html.find(c_value) != -1:
                        return smp
        return None

    def extracts_link(self, linkExraction_list, html):
        for theLinkExtraction in linkExraction_list:
            parent_layout = self.ro.get_sm_parent_layout(theLinkExtraction)
            extraction_rule = self.ro.get_sm_link_selector(theLinkExtraction)
            #'Data scraping from a web page'
            if parent_layout == '*':
                l = self.extract_link_all_html(extraction_rule, html)
                if len(l) > 0:
                    new_links = list(set(l))  # set eliminate duplicate record
                    self.add_web_site_information_to_url(new_links)
            else:
                links_parts = self.extract_link_parent_layouts(parent_layout, html)
                for part_html in links_parts:
                    l = self.extract_link_all_layout(extraction_rule, part_html)
                    if len(l) > 0:
                        new_links = list(set(l))  # set eliminate duplicate record
                        self.add_web_site_information_to_url(new_links)
        return

    @timeit(loop = 250)
    def extract_link_parent_layouts(self, rule, html):  
    #'all link extraction process new function for performance / time operations, in order to save time results.'
        if self.type == 'text-based':
            return re.findall(rule, html, re.DOTALL)
        elif self.type == 'dom' or self.type == 'selenium':
            return html.select(rule)

    @timeit(loop = 250)
    def extract_link_all_html(self, rule, html):
        if self.type == 'text-based':
            return re.findall(rule, html, re.DOTALL)
        elif self.type == 'dom' or self.type == 'selenium':
            return self.get_href(html.select(rule))

    @timeit(loop = 250)
    def extract_link_all_layout(self, rule, html):
        if self.type == 'text-based':
            return re.findall(rule, html, re.DOTALL)
        elif self.type == 'dom' or self.type == 'selenium':
            return self.get_href(html.select(rule))  ##hata var

    def get_href(self, new_links):
        'get href from a dom elemement'
        for ind in range(len(new_links)):
            new_links[ind] = new_links[ind].get('href')
        return new_links

    def add_web_site_information_to_url(self, new_links):
        for ind in range(len(new_links)):
            if new_links[ind] != None and len(new_links[ind]):
                if not (new_links[ind].startswith("http:") or new_links[ind].startswith("https:") or new_links[ind].startswith("//")):
                    # add http and web site name to link, (/.../..../) -> http://website/.../..../
                    # This is an additional control for the links that starts with /,

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
                # add record to frontier
                if new_links[ind] not in self.frontier and new_links[
                    ind] not in self.visited:  # to prevent duplicate links
                    self.frontier[new_links[ind]] = 1
        return

    def stripHtmltag(self, data_list):
        'remove html tags'
        for i in range(len(data_list)):
            data_list[i] = re.sub('<.*?>', '', data_list[i])
        return data_list

    def apply_filters(self, temp_data, theRule, result_type):  # tempdata: list
        'removing, replacing ...'
        temp_data = [str(x) for x in temp_data]  # all values in str format
        html_filter = self.ro.get_sm_extraction_html_filter(theRule)
        if html_filter == 'on':
            temp_data = self.stripHtmltag(temp_data)
        rem_filter = self.ro.get_sm_extraction_rem_filter(theRule)  # list
        for temp_str in rem_filter:
            for i in range(len(temp_data)):
                temp_data[i] = temp_data[i].replace(temp_str, '')
        alter_filter = self.ro.get_sm_extraction_alter_filter(theRule)  # dictionary
        for i in range(len(temp_data)):
            for key, value in alter_filter.items():
                if temp_data[i].find(key) != -1:
                    temp_data[i] = value
                    break
        return temp_data
