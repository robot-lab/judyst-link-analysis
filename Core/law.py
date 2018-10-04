import os.path
import urllib.request
import pdfminer.high_level  # python -m pip install pdfminer.six
import lxml.html as html  # python -m pip install lxml
from selenium import webdriver
  

def GetWebDriver(pathToChromeWebDriver='Core\\Selenium\\chromedriver.exe',
         pageUri = "http://www.ksrf.ru/ru/Decision/Pages/default.aspx"):
    driver = webdriver.Chrome(pathToChromeWebDriver)
    driver.get(pageUri)
    return driver



def GetOpenPageScriptTemplate(driver, templateKey='NUMBER'):
    page = html.document_fromstring(driver.page_source)
    td_list = page.find_class('UserSectionFooter ms-WPBody srch-WPBody')[0]. \
        getchildren()[0]. \
        getchildren()[0]. \
        getchildren()[0]. \
        getchildren()[0]. \
        getchildren()
    
    template = td_list[-1].getchildren()[0].get('href')
    template = template.split(':')[1]
    template = template.split(',')[0] + ',\'Page$' + templateKey + '\');'
    
    return template

def GetOpenPageScript(scriptTemplate, pageNum, templateKey='NUMBER'):
    return scriptTemplate.replace(templateKey, str(pageNum))


def GetPageHtmlByNum(driver, openPagetScriptTemplate, pageNum):
    script = GetOpenPageScript(openPagetScriptTemplate, pageNum)
    driver.execute_script(script)
    return driver.page_source





  
def GetResolutionHeaders(countOfPage = 100):
    court_site_content = {}
    driver = GetWebDriver()
    template = GetOpenPageScriptTemplate(driver)
    page = html.document_fromstring(driver.page_source)

    #repeated_uids = []
    for i in range(2,countOfPage + 2):
        decisions = page.find_class('ms-alternating') + \
                page.find_class('ms-vb')
        for d in decisions:
            decision_id = d[2].text_content()
            #if (decision_id in court_site_content):
                #if (not decision_id in repeated_uids):
                    #repeated_uids.append(decision_id)

            court_site_content[decision_id] = {}
            court_site_content[decision_id]['date'] = d[0].text_content()
            court_site_content[decision_id]['title'] = d[1].text_content()
            court_site_content[decision_id]['url'] = \
                d[2].getchildren()[0].get('href')
        page = html.document_fromstring(GetPageHtmlByNum(driver, template, i))
    
    return court_site_content
    #return court_site_content, repeated_uids




def GetdecisionFileNameByUid(uid, foldername, ext='txt'):
    return os.path.join(foldername, uid.replace('/', '_') + '.' + ext)


def LoadResolutionTexts(court_site_content, folderName='Decision files'):
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    for decision_id in court_site_content:
        logo = urllib.request.urlopen(
                court_site_content[decision_id]['url']).read()
        path_to_pdf = GetdecisionFileNameByUid(decision_id, folderName, 'pdf')
        path_to_txt = GetdecisionFileNameByUid(decision_id, folderName, 'txt')
        with open(path_to_pdf, "wb") as pdf_file:
            pdf_file.write(logo)
        with open(path_to_pdf, "rb") as pdf_file, \
                open(path_to_txt, 'wb') as txt_file:
            pdfminer.high_level.extract_text_to_fp(pdf_file, txt_file)
        court_site_content[decision_id]['url'] = path_to_txt
        os.remove(path_to_pdf)
    return court_site_content




if __name__ == '__main__':
    import json
    #court_site_content = GetResolutionHeaders()
    #court_site_content = LoadResolutionTexts(court_site_content)
    #print(court_site_content)
    #driver = GetWebDriver()
    #template = GetOpenPageScriptTemplate()
    res, repeated = GetResolutionHeaders(1570)
    file = open('repeated.json', 'w')
    file.write(json.dumps(repeated))
    file.close()