import json
import regex_generator as rg

class rules:
    'read the rule file in json format' 
    def __init__(self, filename):
        self.data = self.get_rulefile(filename)

    def get_rulefile(self, filename):
        data = ''
        with open(filename) as json_file:  
            data = json.load(json_file)
        return data
        
    def get_project_name(self):
        if self.data != '':           
            return self.data.get('project_name', 'empty')
        else:
            return ''

    def get_web_site(self):
        if self.data != '':
            temp = self.data.get('web_site', 'empty')
            if temp[len(temp)-1] != '/': #developer can forget this charcter
                temp += '/'
            return temp
        else:
            return ''
    
    def get_seeds(self):
        if self.data != '':
            temp = self.data.get('seeds', [self.get_web_site()])
            if temp == []:
                temp = [self.get_web_site()]
            return temp
        else:
            return ''

    def get_type(self):
        if  self.data != '':
            return self.data.get('type', 'dom') #text-based
        else:
            return ''
    
    def get_wait(self):
        if self.data != '':
            try:
                return int(self.data.get('wait', '0'))
            except:
                return 0
        else:
            return 0
    def get_browser(self):
        if self.data != '':
            return self.data.get('browser', '')
        else:
            return ''
    def get_driver(self):
        if self.data != '':
            return self.data.get('driver', '')
        else:
            return ''
    def get_scrollcount(self):
        if self.data != '':
            return self.data.get('scrolldownfor', '0')
        else:
            return ''

    def get_result_file(self):
        if self.data != '':
            return self.data.get('result_file', 0)
        else:
            return ''

    def get_sitemap(self):
        if self.data != '':
            return self.data.get('sitemap', [])
        else:
            return ''

    def get_sm_page(self, theSitemap):
        if theSitemap != '':
            return theSitemap.get('page', 'MyPage')
        else:
            return ''

    def get_sm_detection(self, theSitemap):
        if theSitemap != '':
            return theSitemap.get('detection', {'url': ''}) #return dictionary: one key, one value
        else:
            return ''

    def get_sm_data_extraction(self, theSitemap):
        if theSitemap != '':
            return theSitemap.get('data_extraction', [])
        else:
            return ''
    
    def get_sm_link_extraction(self, theSitemap):
        if theSitemap != '':
            return theSitemap.get('link_extraction', []) #return list
        else:
            return ''
    
    def get_sm_parent_layout(self, theLinkorData):
        if theLinkorData != '':
            temp = theLinkorData.get('parent_layout', '*')
            temp_reg = theLinkorData.get('parent_layout_regex', '')

            if self.get_type() == 'text-based' and temp != '*':
                if temp_reg == '':
                    temp = rg.csstoRegex(temp)
                else:
                    temp = temp_reg
            return temp
        else:
            return ''
    
    def get_sm_link_selector(self, theLink):
        if theLink != '':
            temp = theLink.get('selector', 'a')
            if self.get_type() == 'text-based':
                temp = rg.ahreftoRegex(temp)
            return temp
        else:
            return ''
    
    def get_sm_extraction_rules(self, Rules):
        if Rules != '':
            return Rules.get('extraction_rules', [])
        else:
            return ''
    
    def get_sm_extraction_rule_name(self, theRule):
        if theRule != '':
            return theRule.get('name', 'Empty')
        else:
            return ''

    def get_sm_extraction_result_type(self, theRule):
        if theRule != '':
            return theRule.get('result_type', 'innerHTML')
        else:
            return ''
    
    def get_sm_extraction_html_filter(self, theRule):
        if theRule != '':
            return theRule.get('html_filter', 'on')
        else:
            return ''
    
    def get_sm_extraction_rem_filter(self, theRule):
        if theRule != '':
            return theRule.get('rem_filter', [])
        else:
            return ''
    
    def get_sm_extraction_alter_filter(self, theRule):
        if theRule != '':
            return theRule.get('alter_filter', {})
        else:
            return ''

    def get_sm_extraction_rule_selector(self, theRule, result_type = 'innerHTML'):
        if theRule != '':
            temp = theRule.get('selector', '')
            temp_reg = theRule.get('selector_regex', '')

            if self.get_type() == 'text-based' and temp != '*':
                if temp_reg == '':
                    temp = rg.csstoRegex(temp, result_type)
                else:
                    temp = temp_reg

            return temp
        else:
            return ''