import os.path

import urllib.request
# License: MIT License

import pdfminer.high_level
# License: MIT License; Installing: python -m pip install pdfminer.six

import lxml.html as html
# License: BSD license; Installing: python -m pip install lxml

from selenium import webdriver
# License: Apache License 2.0


def GetWebDriver(pathToChromeWebDriver='Core\\Selenium\\chromedriver.exe',
                 pageUri="http://www.ksrf.ru/ru/Decision/Pages/default.aspx"):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(pathToChromeWebDriver, chrome_options=options)
    driver.get(pageUri)
    return driver


def GetOpenPageScriptTemplate(driver, templateKey='NUMBER'):
    page = html.document_fromstring(driver.page_source)
    template = page.find_class('UserSectionFooter ms-WPBody srch-WPBody')[0]. \
        find('td/table/tbody/tr/td/a').get('href')
    template = template.split(':')[1]
    template = template.split(',')[0] + ',\'Page$' + templateKey + '\');'
    return template


def GetOpenPageScript(scriptTemplate, pageNum, templateKey='NUMBER'):
    return scriptTemplate.replace(templateKey, str(pageNum))


def GetPageHtmlByNum(driver, openPagetScriptTemplate, pageNum):
    script = GetOpenPageScript(openPagetScriptTemplate, pageNum)
    driver.execute_script(script)
    return driver.page_source


def GetResolutionHeaders(countOfPage=1):
    # TO DO: check for that page is refreshed check for that
    # page is refreshed (i have an idea)
    courtSiteContent = {}
    driver = GetWebDriver()
    template = GetOpenPageScriptTemplate(driver)
    page = html.document_fromstring(driver.page_source)
    for i in range(2, countOfPage + 2):
        decisions = page.find_class('ms-alternating') + \
                page.find_class('ms-vb')
        for d in decisions:
            decisionID = d[2].text_content().upper()
            date = d[0].text_content()
            title = d[1].text_content()
            url = d[2].getchildren()[0].get('href')
            headerElements = {'date': date, 'url': url, 'title': title}
            if decisionID not in courtSiteContent:
                courtSiteContent[decisionID] = headerElements
            else:
                if 'not unique' in courtSiteContent[decisionID]:
                    eggs = False
                    for header in courtSiteContent[decisionID][1]:
                        if header['url'] == url:
                            eggs = True
                            break
                    if not eggs:
                        courtSiteContent[decisionID][1].append(headerElements)
                else:
                    notUniqueHeaders = \
                        [courtSiteContent[decisionID], headerElements]
                    courtSiteContent[decisionID] = \
                        ('not unique', notUniqueHeaders)
        page = html.document_fromstring(GetPageHtmlByNum(driver, template, i))

    return courtSiteContent


def GetdecisionFileNameByUid(uid, foldername, ext='txt'):
    return os.path.join(foldername, uid.replace('/', '_') + '.' + ext)


def LoadResolutionTexts(courtSiteContent, folderName='Decision files'):
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    for decisionID in courtSiteContent:
        if 'not unique' in courtSiteContent[decisionID]:
            continue
        logo = urllib.request.urlopen(
                courtSiteContent[decisionID]['url']).read()
        pathToPDF = GetdecisionFileNameByUid(decisionID, folderName, 'pdf')
        pathToTXT = GetdecisionFileNameByUid(decisionID, folderName, 'txt')
        with open(pathToPDF, "wb") as PDFFIle:
            PDFFIle.write(logo)
        with open(pathToPDF, "rb") as PDFFIle, \
                open(pathToTXT, 'wb') as TXTFile:
            pdfminer.high_level.extract_text_to_fp(PDFFIle, TXTFile)
        courtSiteContent[decisionID]['path to text file'] = pathToTXT
        os.remove(pathToPDF)
    return courtSiteContent


if __name__ == '__main__':
    import json
    # court_site_content = GetResolutionHeaders()
    # court_site_content = LoadResolutionTexts(court_site_content)
    # print(court_site_content)
    # driver = GetWebDriver()
    # template = GetOpenPageScriptTemplate()

    # res, repeated = GetResolutionHeaders(1570)
    # file = open('repeated.json', 'w')
    # file.write(json.dumps(repeated))
    # file.close()

    GetResolutionHeaders(666)
