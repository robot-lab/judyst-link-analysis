__version__ = '0.1'

if __package__:
    from link_analysis.api_module import process_period,\
        start_process_with
    from link_analysis import wc_interface
    from link_analysis import link_handler
    from link_analysis import converters
    from link_analysis.models\
        import Header, DocumentHeader, Link, RoughLink, CleanLink,\
        HeadersFilter, LinkGraph, GraphEdgesFilter,\
        GraphNodesFilter
else:
    from api_module import process_period,\
        start_process_with
    import wc_interface
    import link_handler
    import converters
    from models\
        import Header, DocumentHeader, Link, RoughLink, CleanLink,\
        HeadersFilter, LinkGraph, GraphEdgesFilter,\
        GraphNodesFilter


def Init(databaseSource):
    '''
    Initialize link_analisis
    '''
    wc_interface.init(databaseSource=databaseSource)


__all__ = ['Init', 'Header', 'DocumentHeader', 'Link', 'RoughLink',
           'CleanLink', 'HeadersFilter', 'LinkGraph',
           'GraphEdgesFilter',
           'GraphNodesFilter', 'process_period', 'start_process_with']
