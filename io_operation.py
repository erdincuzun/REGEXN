import os

import requests #download images
import shutil
import imagesize #image dimensions
import re #for getting img>src

class io_operation:
    'dosya işlemleri sınıfı'
    def __init__(self, project_name):
        self.path = os.getcwd()
        #TODO: Fix compability of the directory structure on Linux and Mac
        self.project_path = self.path + "/" + project_name + "/"
        self.project_webpath = self.project_path + "webpages/"
        if not os.path.exists(self.project_path):    
            os.mkdir(self.project_path)
        if not os.path.exists(self.project_webpath):
            os.mkdir(self.project_webpath)  

    def file_count_in_directory(self):
        return len([name for name in os.listdir(self.project_webpath) if os.path.isfile(os.path.join(self.project_webpath, name))])
    
    def save_html_file(self, html):
        sayi = self.file_count_in_directory() + 1
        fn = self.project_webpath + str(sayi).zfill(3) + ".html"
        with open(fn, "w", errors='ignore') as myfile:
            myfile.write(html)
    
    def download_image(self, img_url):
        return requests.get(img_url, stream=True)

    def download_save_file(self, imgs, web_site, type):
        #directory settings
        sayi = self.file_count_in_directory()
        fn = self.project_webpath + str(sayi).zfill(3)
        if not os.path.exists(fn):
            os.mkdir(fn)
        
        imgs = list(set(imgs))
        #dom-based solution, all image elements 
        temp_data = []
        for i in range(len(imgs)):
            print(imgs[i])
            src = ""
            if type == 'text-based':
                matches = re.search('src\\s*=\\s*\\\\*"(.+?)\\\\*"', imgs[i]) #TODO:Testing...
                src = matches[0]
            else: #'dom' or 'selenium':
                if 'src' in imgs[i].attrs:
                    src = imgs[i]['src'] #get a src attributes of the element
                    if src == "":
                        if 'data-src' in imgs[i].attrs:
                            src = imgs[i]['data-src']
                else:
                    if 'data-src' in imgs[i].attrs:
                            src = imgs[i]['data-src']
                
            
            if src != "":
                last_ch = src.rfind('/')
                filename = src[last_ch + 1:]
                filename = filename.replace("=", "_").replace("/", "_").replace("\\", "_").replace("?", "_").replace("&", "_").replace("%", "_")
                if len(filename)>40:
                    filename = filename[-40:]
                if os.path.exists(fn + '/' + filename):
                    filename = src[src[:last_ch-1].find('/') + 1:]
                    filename = filename.replace("=", "_").replace("/", "_").replace("\\", "_").replace("?", "_").replace("&", "_").replace("%", "_")
                    if len(filename)>50:
                        filename = filename[-50:]
                
                
                ind = src.rfind('../')
                img_url = src
                if ind >= 0:
                    img_url = web_site + src[ind + 3:] #add website to ../
                if src.find('/') == 0:
                    img_url = web_site + src[1:]

                if not 'data:' in img_url:
                    r = self.download_image(img_url)
                    if r.status_code == 200: #image file is ok
                        with open(fn + '/' + filename, 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)
                        width, height = imagesize.get(fn + '/' + filename)
                        filesize = os.path.getsize(fn + '/' + filename)
                        tmp_str = img_url + ',' + str(width) + ',' + str(height) + ',' + str(filesize)
                        temp_data.append(tmp_str)
                        with open(fn + '/image_urls.txt', 'a', errors='ignore') as myfile:
                            myfile.write(tmp_str + '\n')
                else:
                    print(">>>HATA: " + img_url)
        return temp_data

    def save_extraction_results(self, rows, filename="outputs"):
        fn = self.project_path + filename + ".txt"
        with open(fn, "a", errors='ignore') as myfile:
            for row in rows:
                if row != None:
                    myfile.write(row + "\n")

    def preparedatatoSave(self, result):
        'data preaparing to save, rows, simple csv file'
        temp = []
        for key in result.keys():
            if len(temp) == 0:
                temp = result[key]
            else:
                for ind in range(len(result[key])):
                    try:
                        temp[ind] += "," + result[key][ind]
                    except:
                        continue
        return temp