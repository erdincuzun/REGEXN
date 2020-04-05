def extract(pattern, html, startIndex, endtag_cnt, repeative):
    start_tn = start_TagName(pattern)
    end_tn = end_TagName(pattern)
    list_result = []
    start_ind = html.find(pattern, startIndex)
    if(start_ind == -1):
        start_ind = html.find(pattern, 0)
    if(start_ind != -1):
        end_ind = html.find(end_tn, start_ind + len(pattern)) + len(end_tn)
        result_tmp = ''
        start_tag = 0
        end_tag = 0
        if (endtag_cnt > -1):
            start_tag = endtag_cnt
        while True:
            sub_tmp = html[start_ind:end_ind]            
            result_tmp += sub_tmp
            end_tag += 1
            if(endtag_cnt == -1):
                start_tag += sub_tmp.count(start_tn)
            if(start_tag != end_tag):
                start_ind = end_ind
                end_ind = html.find(end_tn, start_ind) + len(end_tn)
                if (end_ind == -1):
                    return list_result #unexpected error
            else:
                list_result.append(result_tmp)
                if (repeative == False):
                    break
                start_ind = html.find(pattern, end_ind)
                if (start_ind == -1):
                    break
                end_ind = html.find(end_tn, start_ind + len(start_tn)) + len(end_tn)
                result_tmp = ""
                if (endtag_cnt > -1):
                    start_tag = endtag_cnt
                else:
                    start_tag = 0
                end_tag = 0
        #while end
        return list_result
    else:
        return list_result

def parse_TagName(element):
    return element[(element.find('<') + 1):(element.find(' '))]

def start_TagName(element):
    return '<' + parse_TagName(element)

def end_TagName(element):
    return '</' + parse_TagName(element) + '>'
