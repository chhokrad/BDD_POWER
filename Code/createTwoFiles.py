import xml.etree.ElementTree as ET
import os.path

def createTwoFiles(filename):
    newfiles = []
    for i in range(0,2):
        if i == 0:
            flag =  True
        else:
            flag = False
        xmlobject = ET.parse(filename)
        root  =  xmlobject.getroot()
        parent_map = dict((c, p) for p in xmlobject.getiterator() for c in p)
        iterator = list(root.getiterator('Final_Stage'))

        for item in iterator:
            if item.text == 'Safe' and flag:
                parent_map[parent_map[item]].remove(parent_map[item])
            elif item.text == 'Blackout' and not flag:
                parent_map[parent_map[item]].remove(parent_map[item])
        file_name = filename[:-4] + '_' + str(flag) +'.xml'
        xmlobject.write(file_name)
        newfiles.append(file_name)
    return newfiles

if __name__ == '__main__':
    #xmlfile = 'ieee14bus_system2.xml'
    #xmlfile  = 'ieee39bus_system2.xml'
    xmlfile = 'ieee57bus_system_N-2.xml'
    os.chdir('/Users/ajaychhokra/Documents/workspace/prognostics/NEWDATA')
    print(createTwoFiles(xmlfile))
