from SymbolicModelCheckerWOS import *
from SymbolicModelCheckerLFF import *
import timeit
import xml.etree.ElementTree as ET
from collections import OrderedDict
import matplotlib.pyplot as plt
import os

def transformXMLfile(xmlfile):
    xmlobject = ET.parse(xmlfile)
    root = xmlobject.getroot()
    for outage in root.iter('Outage'):
        temp = re.sub(r'Line\.|Transformer\.','',outage.text)
        if temp is not None:
            outage.text = temp
    newfilelabel = '_'+xmlfile
    xmlobject.write(newfilelabel)
    return newfilelabel


def transformXMLfile_(xmlfile):
    xmlobject = ET.parse(xmlfile)
    root = xmlobject.getroot()
    for tripping in root.iter('Tripping'):
        temp = re.sub(r'Line\.|Transformer\.','',tripping.text)
        if temp is not None:
            tripping.text = temp
    newfilelabel = '_'+xmlfile
    xmlobject.write(newfilelabel)
    return newfilelabel



if __name__ == '__main__':
    '''
    linelables = ['tl87','tl139','tl12','tl939','tl89','tl58',
                    'tl67','tl65','tl54','tl34','tl23','tl225',
                    'tl2526','tl318','tl1817','tl1727','tl2726',
                    'tl1617','tl1516','tl1415','tl414','tl1413',
                    'tl1013','tl1011','tl611','tl2628','tl2829',
                    'tl2629','tl1624','tl1621','tl2122','tl1619',
                    'tl2223','tl2423', 't1', 't2', 't3', 't4',
                    't5', 't6', 't7', 't8', 't9', 't10', 't11', 't12']
    '''
    os.chdir('/Users/ajaychhokra/Documents/workspace/prognostics/NEWDATA')
    NumCasesPos = 300
    NumCasesNeg = 700
    '''
    linelables = ['tl12', 'tl1011', 'tl1213', 'tl25', 'tl34', 'tl24', 'tl47',
                'tl15', 'tl914', 'tl49', 'tl612', 'tl23', 'tl1314', 'tl910',
                'tl611', 'tl79', 'tl78', 'tl45', 'tl56', 'tl613']
    '''
    linelables = ['tl5253','tl2627','tl4950','tl117','tl5455','tl5354',
                    'tl2952','tl78','tl89','tl68','tl67','tl56','tl45','tl46','tl34','tl23',
                    'tl2829','tl2728','tl2425a','tl2425b','tl2530','tl3031','tl1819','tl1920',
                    'tl2122','tl2223','tl2324','tl12','tl116','tl1216','tl1217','tl912','tl910',
                    'tl115','tl315','tl1415','tl4445','tl3844','tl2238','tl3738','tl3637',
                    'tl3536','tl3435','tl3132','tl3233','tl4647','tl4748','tl3848','tl4849',
                    'tl3849','tl3739','tl3640','tl5756','tl5641','tl4143','tl911','tl913',
                    'tl4142','tl5642','tl1113','tl1315','tl1314','tl1213','tl1012','tl5051', 'transformer1', 'transformer2',
                    'transformer3', 'transformer4',
                    'transformer5', 'transformer6', 'transformer7', 'transformer8',
                    'transformer9', 'transformer10', 'transformer11',
                    'transformer12', 'transformer13', 'transformer14', 'transformer15']

    print('variables', len(linelables))
    linelables_dict = OrderedDict()
    for label in linelables:
        linelables_dict[label] = 1
    linelables_dict_copy = OrderedDict()

    #xmlfileTrue = '39BusBlackOutCases_True.xml'
    #xmlfileFalse = '39BusBlackOutCases_False.xml'

    xmlfileTrue = 'ieee57bus_system_N-2_True.xml'
    xmlfileFalse = 'ieee57bus_system_N-2_False.xml'


    # transforming the xml file in main function
    xmlfileTrue = transformXMLfile(xmlfileTrue)
    xmlfileFalse = transformXMLfile(xmlfileFalse)
    #xmlfileFalse = transformXMLfile_(xmlfileFalse)
    #xmlfileFalse = '_14BusSystemFalse.xml'

    start = timeit.default_timer()
    myBlackoutDS1 = blackout_BDD(linelables, xmlfileTrue)
    stop = timeit.default_timer()
    print('size of bdd_1', len(myBlackoutDS1.bdd_initiatingEvents), 'size of bdd_2', len(myBlackoutDS1.bdd_transitionRelation))

    print('****************************************')
    print('Time to build BDDs :' + str(stop - start))
    print('****************************************')

    # Checking every true case and storing the time required for calculating the trace
    True_positives = 0
    True_negatives = 0
    False_positives = 0
    False_negatives = 0
    True_positive_time = list()
    True_negative_time = list()
    True_positive_stage = list()
    root  = ET.parse(xmlfileTrue).getroot()
    pos_counter = 0
    for initial in root.iter('Initial_Stage'):
        pos_counter += 1
        linelables_dict_copy = linelables_dict.copy()
        for outage in initial.iter('Outage'):
            linelables_dict_copy[outage.text] = 0
        start = timeit.default_timer()
        answer  = myBlackoutDS1.checkSystemState(linelables_dict_copy)
        stop = timeit.default_timer()
        if (answer != False and (stop - start) > 0.030):
            print('Abnormal query time ', (stop-start), linelables_dict_copy)
        if answer !=  False:
            True_positive_time.append(stop - start)
            True_positive_stage.append(len(answer)-1)
            True_positives = True_positives + 1
        else:
            False_positives = False_positives + 1
        if pos_counter == 300:
            break

    print('----------------------------------------------------------------------')
    print('True case Statistics (i.e. initiating events that lead to blackout)')
    print('Numer of true positives :' + str(True_positives))
    print('Number of false positives :' + str(False_positives))
    print('----------------------------------------------------------------------')
    fig = plt.figure()
    ax = fig.add_subplot(211)
    ax.set_title('True Positives')
    #ax.set_xlabel('N-k contengencies')
    ax.set_ylabel('Time in seconds')
    ax.text(0.8, 0.8, 'Average time is :' + str(round((sum(True_positive_time) / float(len(True_positive_time))),4)),
        horizontalalignment='right',
        verticalalignment='top',
        transform=ax.transAxes)
    True_positive_time = sorted(True_positive_time)
    ax.stem(True_positive_time)
    #fig.savefig('TruePositive.png')



    root  = ET.parse(xmlfileFalse).getroot()
    neg_counter = 0
    for initial in root.iter('Initial_Stage'):
        neg_counter += 1
        linelables_dict_copy = linelables_dict.copy()
        for outage in initial.iter('Outage'):
            linelables_dict_copy[outage.text] = 0
        start = timeit.default_timer()
        answer  = myBlackoutDS1.checkSystemState(linelables_dict_copy)
        stop = timeit.default_timer()
        if answer ==  False:
            True_negative_time.append(stop - start)
            True_negatives = True_negatives + 1
        else:
            False_negatives = False_negatives + 1
        if neg_counter == 700:
            break

    print('----------------------------------------------------------------------')
    print('False case Statistics (initiating events that do not lead to blackout)')
    print('Numer of true negatives :' + str(True_negatives))
    print('Number of false negatives :' + str(False_negatives))
    print('----------------------------------------------------------------------')
    #fig1 = plt.figure()
    ax = fig.add_subplot(212)
    ax.set_title('True Negatives')
    ax.set_xlabel('N-k contingencies')
    ax.set_ylabel('Time in seconds')
    ax.text(0.8, 0.8, 'Average time is :' + str(round((sum(True_negative_time) / float(len(True_negative_time))), 6)),
        horizontalalignment='right',
        verticalalignment='top',
        transform=ax.transAxes)
    True_negative_time = sorted(True_negative_time)
    ax.stem(True_negative_time)
    fig.savefig(xmlfileTrue[:-10] + '.png')
