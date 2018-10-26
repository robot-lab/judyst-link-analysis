__version__ = '0.1'

if __package__:
    from link_analysis.api_module import process_period,\
        start_process_with
    from link_analysis import wc_interface
    from link_analysis import rough_analysis
    from link_analysis import final_analysis
    from link_analysis import converters
    from link_analysis.models\
        import Header, DocumentHeader, Link, RoughLink, CleanLink,\
        HeadersFilter, LinkGraph, IterableLinkGraph, GraphEdgesFilter,\
        GraphNodesFilter
else:
    from api_module import process_period,\
        start_process_with
    import wc_interface
    import rough_analysis
    import final_analysis
    import converters
    from models\
        import Header, DocumentHeader, Link, RoughLink, CleanLink,\
        HeadersFilter, LinkGraph, IterableLinkGraph, GraphEdgesFilter,\
        GraphNodesFilter


def Init(databaseSource):
    '''
    Initialize link_analisis
    '''
    wc_interface.init(databaseSource=databaseSource)


__all__ = ['Init', 'Header', 'DocumentHeader', 'Link', 'RoughLink',
           'CleanLink', 'HeadersFilter', 'LinkGraph',
           'IterableLinkGraph', 'GraphEdgesFilter',
           'GraphNodesFilter', 'process_period', 'start_process_with']
