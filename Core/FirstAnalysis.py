import re
import os 
def FirstAnalysis(str, ALL):
    file = open(str,'r')
    R = file.read()
    file.close()
    n = R.find('Мнение судьи Конст')
    R = R[0:n]

    pattern = re.compile(r'[Оо].\s\d+\s[яфмаисонд]\w+\s\d+\sгода\s№\s\d[^ ),]+')
    result = pattern.findall(R)
    #print (result)
    ALL[str] = result

if __name__ == "__main__":    
    files = os.listdir()
    texts = filter(lambda x: x.endswith('.txt'), files)
    ALL = {} 
    for text in texts:
        FirstAnalysis(text,ALL) 
        print (ALL)