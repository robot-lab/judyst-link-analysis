# Judist link analysis.
Этот репозиторий посвящен компоненте анализа ссылок в юридических документах. Посетите [wiki](https://github.com/robot-lab/judyst-link-analysis/wiki) для получения большей информации. 
 ***
 Последняя стабильная ветка - LastVersion
 Инструкция по по использованию:
 
 ### Установка
 
 1. Установить [web_crawler](https://github.com/robot-lab/judyst-web-crawler)
 2. Установить link_analysis через pip ([этот файл](https://github.com/robot-lab/judyst-link-analysis/blob/LastVersion/dist/link_analysis-0.1-py3-none-any.whl))
 
 
 ### Использование
 
 Перед работой с модулем необходимо выполнить инициализацию модуля источником данных. Источником данных может являться любой объект, следующий интерфейсу web_crawler.DataSource 

 Так, например, можно инициализировать link_analysis для работы с базой данных. "точкой соединения" с базой данных является объект [ModelData](https://github.com/robot-lab/judyst-main-web-service/blob/master/celery/data.py)
 
 ```
import link_analysis as la
from web_crawler import DatabaseWrapper
from data import ModelData
model = ModelData()
source = DatabaseWrapper("data-source-name", model)
la.Init(source)
 ```
 
 
 
 ***
[Команда](https://github.com/robot-lab/judyst-main-web-service/wiki/Team-members)

 [Репозиторий проекта](https://github.com/robot-lab/judyst-main-web-service)
