import regex_generator as rg
import read_rules as rr

#Regular Expression Tester: pattern is suitable for extraction or not?

def test1():
    'regex_generator tests'
    # print(rg.csstoRegex("div"))
    # print(rg.csstoRegex("div#idexample"))
    # print(rg.csstoRegex("div.classexample"))    
    # print(rg.csstoRegex("div[item='otherattribute']"))
    # print(rg.csstoRegex("div#idexample.classexample"))
    # print(rg.csstoRegex("div.classexample[item='otherattribute']"))
    #a href, link extraction
    print(rg.ahreftoRegex("a"))
    # print(rg.ahreftoRegex("a.test1"))
    # print(rg.ahreftoRegex("a#test2"))
    # print(rg.ahreftoRegex("a[test='deneme']"))
    # print(rg.ahreftoRegex("a.test1#test2"))
    # print(rg.ahreftoRegex("div#test1.test2"))
    #print(rg.csstoRegex("a[href='test']"))

    print(rg.csstoRegex("div#main_content"))
    print(rg.csstoRegex("div.content1"))
    print(rg.csstoRegex("div.content2"))


def test2():
    'test rule.json file'
    ro = rr.rules("rules.json")
    print(ro.data['project_name'])
    print(ro.get_project_name())
    print(ro.get_web_site())
    print(ro.get_seeds()) #return list
    print(ro.get_type())
    print(ro.get_wait()) 
    print(len(ro.get_sitemap())) #list len     
    theSitemap = ro.get_sitemap()[2]    
    print(ro.get_sm_page(theSitemap))    
    print(ro.get_sm_detection(theSitemap))   
    theData = ro.get_sm_data_extraction(theSitemap) 
    print(theData)
    print(ro.get_sm_parent_layout(theData[0]))
    theRule = ro.get_sm_extraction_rules(theData[0])
    print(theRule[0])
    print(ro.get_sm_extraction_rule_name(theRule[0]))
    print(ro.get_sm_extraction_rule_selector(theRule[0]))
    theLink = ro.get_sm_link_extraction(theSitemap)[0]
    print(theLink)
    print(ro.get_sm_parent_layout(theLink))
    print(ro.get_sm_link_selector(theLink))



test1()
#test2()

import regex_end_finder as ref
import re

html = """<div><div><div><div id="deneme">
  <h3>This is a heading</h3>
  <p>This is a paragraph.</p>
  <div class="myclass">
    <div id="denemet">
    <h3>This is a heading</h3>
    <p>This is a paragraph.</p>
    </div>...</div>...</div> 
    <div id="last"> deneme </div> </div> </div>
    """ 
# pattern1 = rg.csstoRegex("div#deneme", "HTMLtag")
# print(pattern1)
# sonuc = re.search(pattern1, html, re.DOTALL)
# print(sonuc)
# if sonuc != None:
#   sonuc = sonuc.group()
#   endp, sonuc = ref.find_uniqueEndPattern(sonuc, html)
  # print(endp)
  # output = re.findall(pattern1 + "(.*?)" + endp, html, re.DOTALL)
  # print("endp:" + endp)
  # print("pattern: " + pattern1 + "(.*?)" + endp)
  # print(output)
