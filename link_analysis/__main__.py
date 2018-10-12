def main():
    # import time
    # import link_analysis.api_module as api
    # # ProcessPeriod("01.07.2018", "30.12.2018")
    # # ProcessPeriod("17.07.2018", "17.07.2018", isNeedReloadHeaders=False)
    # # LoadAndVisualize()
    # # CollectHeaders()
    # start_time = time.time()
    # api.process_period("18.06.1980", "18.07.2020", showPicture=False,
    #                    isNeedReloadHeaders=False)
    # #  start_process_with('1671-О-Р/2018', 10)
    # print("--- {0} seconds ---".format(time.time() - start_time))
    # input('press any key to close...')
    import web_crawler
    web_crawler.__main__.main()
main()
