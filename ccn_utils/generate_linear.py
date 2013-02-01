#!/usr/bin/python

import optparse

def parse_args():
    usage="""Usage: generate_linear num_nodes [template_file] [delay]
    Generates template_file with a linear topology with num_nodes and 
    delay in the links (10ms, 100ms, etc).If no template_file is given,
    will write to default file miniccnx.conf in the current directory. 
    """

    parser = optparse.OptionParser(usage)

    _, arg = parser.parse_args()
    
    if len(arg) > 3:
        print parser.usage
        quit()
    elif len(arg) == 0:
        print parser.usage
        quit()
    elif len(arg) == 1:
        num_nodes = int(parser.parse_args()[1][0])
        temp_file = ''
        delay = ''
    elif len(arg) == 2:
        num_nodes, delay = int(parser.parse_args()[1][0]), parser.parse_args()[1][1]
        temp_file = ''
    else:
        print parser.parse_args()
        num_nodes,temp_file, delay = int(parser.parse_args()[1][0]), parser.parse_args()[1][1],parser.parse_args()[1][2]
    
    return num_nodes, temp_file, delay

if __name__ == '__main__':
    
    n_nodes, t_file, delay = parse_args()
    
    if t_file == '':
        t_file = 'miniccnx.conf'
        
    temp_file = open(t_file,'w')
    
    temp_file.write('[hosts]\n')

    temp_file.write('[routers]\n')
    
    for i in range(n_nodes):
        if i == (n_nodes - 1):
            temp_file.write('s' + str(i) + ':\n')
        else:
            temp_file.write('s' + str(i) + ': ccnx:/,s' + str(i+1) + '\n')
        
    temp_file.write('[links]\n')
        
    for i in range(n_nodes-1):
        peer = i + 1
        if delay == '':
            temp_file.write('s' + str(i) + ':s' + str(peer) + '\n')
        else:
            temp_file.write('s' + str(i) + ':s' + str(peer) + ' delay=' + delay +'\n')
            
    temp_file.close()
