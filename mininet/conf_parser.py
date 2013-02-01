import ConfigParser

class confCCNHost():
    
    def __init__(self, name, app='', uri_tuples=''):
        self.name = name
        self.app = app
        self.uri_tuples = uri_tuples
        
    def __repr__(self):
        return 'Name: ' + self.name + ' App: ' + self.app + ' URIS: ' + str(self.uri_tuples) 

class confCCNLink():
    
    def __init__(self,h1,h2,linkDict=None):
        self.h1 = h1
        self.h2 = h2
        self.linkDict = linkDict
        
    def __repr__(self):
        return 'h1: ' + self.h1 + ' h2: ' + self.h2 + ' params: ' + str(self.linkDict)
    
def extrai_hosts(conf_arq):
    'Extrai hosts da secao hosts do arquivo de configuracao'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)
    
    hosts = []
    
    items = config.items('hosts')
    
    for item in items:

        name = item[0]
  
        rest = item[1].split()

        app = rest.pop(0)
        
        uris = rest
        uri_list=[]
        for uri in uris:
            uri_list.append((uri.split(',')[0],uri.split(',')[1]))
        
        hosts.append(confCCNHost(name , app, uri_list))
    
    return hosts

def extrai_routers(conf_arq):
    'Extrai routers da secao routers do arquivo de configuracao'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)

    routers = []
    
    items = config.items('routers')
    
    for item in items:
        name = item[0]
  
        rest = item[1].split()

        uris = rest
        uri_list=[]
        for uri in uris:
            uri_list.append((uri.split(',')[0],uri.split(',')[1]))
        
        routers.append(confCCNHost(name=name , uri_tuples=uri_list))
    
    return routers

def extrai_links(conf_arq):
    'Extrai links da secao links do arquivo de configuracao'
    arq = open(conf_arq,'r')
    
    links = []
     
    while True:
        line = arq.readline()
        if line == '[links]\n':
            break
    
    while True:
        line = arq.readline()
        if line == '':
            break
        
        args = line.split()
        h1, h2 = args.pop(0).split(':')
        
        link_dict = {}
        
        for arg in args:
            arg_name, arg_value = arg.split('=')
            key = arg_name
            value = arg_value
            if key in ['loss','bw','jitter']:
                value = int(value)
            
            link_dict[key] = value
            
        links.append(confCCNLink(h1,h2,link_dict))
        
        
    return links
        
        
    
