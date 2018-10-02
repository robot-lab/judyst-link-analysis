import os.path
import urllib.request
import pdfminer.high_level  # python -m pip install pdfminer.six
import lxml.html as html  # python -m pip install lxml
import selenium.webdriver as webdriver
import time


def SEEHERE():
    driver = webdriver.Firefox()
    driver.get("http://www.ksrf.ru/ru/Decision/Pages/default.aspx")
    # driver.execute_script(r"javascript:__doPostBack('ctl00$m$g_8da72b0e_36c3_43d7_9458_469b90467bbc$gView','Page$2')")
    time.sleep(5)
    page = html.document_fromstring(driver.page_source)
    td_list = page.find_class('UserSectionFooter ms-WPBody srch-WPBody')[0]. \
        getchildren()[0]. \
        getchildren()[0]. \
        getchildren()[0]. \
        getchildren()[0]. \
        getchildren()
    print(type(td_list))
    print(td_list[-1].text_content())
    print(td_list[-1].getchildren()[0].get('href'))


def GetResolutionHeaders(drive_page_source):
    page = html.document_fromstring(drive_page_source)
    decisions = page.find_class('ms-alternating') + \
        page.find_class('ms-vb')
    court_site_content = {}
    for d in decisions:
        decision_id = d[2].text_content()
        court_site_content[decision_id] = {}
        court_site_content[decision_id]['date'] = d[0].text_content()
        court_site_content[decision_id]['title'] = d[1].text_content()
        court_site_content[decision_id]['url'] = \
            d[2].getchildren()[0].get('href')
    return court_site_content


def LoadResolutionTexts(court_site_content, folderName='Decision Files'):
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    for decision_id in sorted(court_site_content):
        logo = urllib.request.urlopen(
                court_site_content[decision_id]['url']).read()
        path_to_pdf = os.path.join(folderName,
                                   decision_id.replace('/', '_') + '.pdf')
        path_to_txt = os.path.join(folderName,
                                   decision_id.replace('/', '_') + '.txt')
        with open(path_to_pdf, "wb") as pdf_file:
            pdf_file.write(logo)
        with open(path_to_pdf, "rb") as pdf_file, \
                open(path_to_txt, 'wb') as txt_file:
            pdfminer.high_level.extract_text_to_fp(pdf_file, txt_file)
        court_site_content[decision_id]['url'] = path_to_txt
        os.remove(path_to_pdf)
    return court_site_content

if __name__ == '__main__':
    driver = webdriver.Firefox()
    driver.get("http://www.ksrf.ru/ru/Decision/Pages/default.aspx")
    court_site_content = GetResolutionHeaders(driver.page_source)
    court_site_content = LoadResolutionTexts(court_site_content)
    print(court_site_content)
