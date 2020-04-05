def csstoRegex(css_selector, result_type = 'innerHTML'):
    pattern_anycharacter = '[\\sa-zA-Z0-9_-]*?'
    pattern_start = '\\s*?[\'"]'
    pattern_end = '[\'"].*?'
    pattern_space = '\\s*'

    pos_id = css_selector.find('#')
    pos_class = css_selector.find('.')
    pos_other_attributes = css_selector.find('[')

    regex = ''
    if pos_class != -1 or pos_id != -1 or pos_other_attributes != -1:
        d = {'id': pos_id, 'class': pos_class, 'other': pos_other_attributes}
        d = {key: d[key] for key in d if d[key] > 0}
        key_min = min(d.keys(), key=(lambda k: d[k]))
        val = d[key_min]
        tagname = css_selector[:val]
        regex = '<' + tagname + pattern_space
        while len(d)>0:
            d.pop(key_min)
            if len(d) > 0: #more than one attribute, the ordering of attributes is a crucial case for regex
                #store last key
                temp_key_min = min(d.keys(), key=(lambda k: d[k]))
                temp_val = d[temp_key_min]
                temp_css = css_selector[val+1: temp_val] #between . and .
            else:
                temp_css = css_selector[val+1:] #between . and end index of string
            
            if not key_min in ['id', 'class']:
                temp_css = css_selector[val + 1 : val + 1 + css_selector[val+1:].find(']')] # between brackets
            
            if key_min in ['id', 'class']:
                if  key_min == 'id': 
                    rep_char = '#'
                else:
                    rep_char = '.' 
                regex += key_min + '=' + pattern_start + pattern_anycharacter 
                regex += temp_css.replace(rep_char, pattern_anycharacter) 
                regex += pattern_anycharacter + pattern_end
            else:
                regex += temp_css.replace('"', pattern_start).replace('\'', pattern_start)

            if len(d) > 0:       
                key_min = temp_key_min
                val = temp_val
        
        if result_type == 'outerHTML':
            regex += '>.*?</' + tagname + '>'
        elif result_type == 'HTMLtag':
            regex += '>'
        else:
            regex += '>(.*?)</' + tagname + '>'
    else: #means css_selector only contains tag name
        if result_type == 'outerHTML':
            regex = '<' + css_selector + '>.*?</' + css_selector + '>'
        elif result_type == 'HTMLtag':
            regex = '<' + css_selector + '>'
        else:
            regex = '<' + css_selector + '>(.*?)</' + css_selector + '>'
    
    return regex

def ahreftoRegex(css_selector):
    if len(css_selector)>=0:
        if css_selector[0] != 'a':
            return ''
        else:
            temp = csstoRegex(css_selector, 'HTMLtag')
            end_pos = temp.find('>')  
            return temp[:end_pos] + '[^>]* href=[\'|"]([^\'|^"]*)["|\']'
    else: 
        return ''