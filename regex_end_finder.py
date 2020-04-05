def extract(pattern, end_pattern, html, startIndex = 0):
    start_ind = html.find(pattern, startIndex)
    if(start_ind != -1):
        end_ind = html.find(end_pattern, (startIndex + len(pattern)))
        if(end_ind != -1):
            end_ind = end_ind + len(end_pattern)
            return html[start_ind:end_ind]
        else:
            return None
    else:
        return None

def find_uniqueEndPattern(pattern, html):
    result_temp, start_tag_pos, end_tag_pos, innerTag = end_index(pattern, html) # first record
    if not innerTag:
        return html[start_tag_pos: end_tag_pos], result_temp #result don't contain inner tags
    start_ind = end_tag_pos + 1 
    while True: #result 
        end_tag_pos = html.find(">", start_ind)
        if end_tag_pos != -1: #check end elemen        
            end_pattern = html[start_tag_pos:end_tag_pos + 1]
            if find_all(html[start_tag_pos:], end_pattern) == 1:
                end_pattern = end_pattern.replace(" ", "\\s").replace("\n",".")
                new_pattern =  pattern + "(.*?)" + end_pattern
                return end_pattern, result_temp, new_pattern
            else:
                start_ind = end_tag_pos + 1
        else:
                return None, ""  #no result
    else:
        return None, "" #no result

def end_index(pattern, html):
    start_tn = start_TagName(pattern)
    end_tn = end_TagName(pattern)
    start_ind = html.find(pattern, 0)
    if(start_ind == -1):
        start_ind = html.find(pattern, 0)
    if(start_ind != -1):
        end_sind = html.find(end_tn, start_ind + len(pattern)) 
        end_ind = end_sind + len(end_tn)
        innertag = False
        result_tmp = ''
        start_tag = 0
        end_tag = 0
        while True:
            sub_tmp = html[start_ind:end_ind]
            result_tmp += sub_tmp
            end_tag += 1
            start_tag += sub_tmp.count(start_tn)
            if(start_tag != end_tag):
                start_ind = end_ind
                end_sind = html.find(end_tn, start_ind)
                end_ind = end_sind + len(end_tn)
                innertag = True
                if (end_sind == -1):
                    return -2 #unexpected error
            else:
                return result_tmp, end_sind, end_ind, innertag #Closing of element
                #for example <div id="deneme"> Test1 <div> Test2 </div> Test3 </div>
                #result_tmp:  Test1 <div> Test2 </div> Test3 : finds the appropriate </div> for a given tag
                #end_sind = gives the position of "<" in the appropriate "<"/div>
                #end_ind =  gives the position of ">" in the appropriate "<"/div>
                #innertag = True: means <div id="deneme"> contains inner "<div" tag, so finding the appropriate "</div" is important
                #innertag = False: means <div id="deneme"> don't contain inner "<div" tag
        #while end
        return -1
    else:
        return -1

def parse_TagName(element):
    return element[(element.find('<') + 1):(element.find(' '))]

def start_TagName(element):
    return '<' + parse_TagName(element)

def end_TagName(element):
    return '</' + parse_TagName(element) + '>'

def find_all(a_str, sub):
    start = 0
    cnt = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return cnt
        cnt += 1
        start += len(sub)