import os.path
import urllib.request
import pdfminer.high_level  # python -m pip install pdfminer.six
import lxml.html as html  # python -m pip install lxml


def GetResolutionHeaders():
    page = html.parse('http://www.ksrf.ru/ru/Decision/Pages/default.aspx')
    decisions = page.getroot().find_class('ms-alternating') + \
        page.getroot().find_class('ms-vb')
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
    court_site_content = GetResolutionHeaders()
    court_site_content = LoadResolutionTexts(court_site_content)
    print(court_site_content)
