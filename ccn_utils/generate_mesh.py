#!/usr/bin/python

import optparse

def parse_args():
    usage="""Usage: generate_mesh num_nodes [template_file]
    Generates template_file with a full mesh topology with num_nodes
    If no template_file is given, will write to default 
    file miniccnx.conf in the current directory.
    """

    parser = optparse.OptionParser(usage)

    _, arg = parser.parse_args()
    
    if len(arg) > 2:
        print parser.usage
        quit()
    elif len(arg) == 0:
        print parser.usage
        quit()
    elif len(arg) == 1:
        num_nodes = int(parser.parse_args()[1][0])
        temp_file = ''
    else:
        print parser.parse_args()
        num_nodes,temp_file = int(parser.parse_args()[1][0]), parser.parse_args()[1][1]
    
    return num_nodes, temp_file

if __name__ == '__main__':
    
    n_nodes, t_file = parse_args()
    
    if t_file == '':
        t_file = 'miniccnx.conf'
        
    temp_file = open(t_file,'w')
    
    temp_file.write('[hosts]\n')

    temp_file.write('[routers]\n')
    
    for i in range(n_nodes):
        temp_file.write('s' + str(i) + ':\n')
        
    temp_file.write('[links]\n')
        
    for i in range(n_nodes):
        peer = i + 1
        for j in range(peer,n_nodes):
            temp_file.write('s' + str(i) + ':s' + str(j) + '\n')
            
    temp_file.close()
            
        
    