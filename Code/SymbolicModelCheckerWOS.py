from dd import autoref as _bdd
import xml.etree.ElementTree as ET
from collections import OrderedDict
import re

class blackout_BDD():
    def __init__(self, varList, simulationData = None ):
        assert(varList != None)
        self.vars = varList # TopologyData is a list of labels associated to variables.
        self.bdd_initiatingEvents = _bdd.BDD()
        self.bdd_transitionRelation = _bdd.BDD()
        self.InitiatingEvents = ""
        self.TransitionRelation = ""
        self.initiatingEventExpr = self.bdd_initiatingEvents.false
        self.transitionRelationExpr = self.bdd_transitionRelation.false
        self.primes = OrderedDict()
        self.qvars = list()
        self.counter = 0
        for var in self.vars:
            self.bdd_initiatingEvents.add_var(var)
            self.bdd_transitionRelation.add_var(var)
            self.bdd_transitionRelation.add_var(var + 'p')
            self.primes[var + 'p'] = var
            self.qvars.append(var)
        if not simulationData is None:
            self.xmlfile = simulationData
            self.createBDDs()

    def updateInitiatingEvents(self, newEvaluation):
        self.initiatingEventExpr = self.initiatingEventExpr | newEvaluation

    def updateTransitionRelation(self, newRelation):
        self.transitionRelationExpr = self.transitionRelationExpr | newRelation

    def createBDDs(self):
        root  = ET.parse(self.xmlfile).getroot()
        for path in root.iter('Path'):
            self.counter = self.counter + 1
            initial_outages = list()
            for Initial_Stage in path.iter('Initial_Stage'):
                for outage in Initial_Stage.iter('Outage'):
                    initial_outages.append(outage.text)
            self.updateInitiatingEvents(self.bdd_initiatingEvents.add_expr(self.getExpressionStringInitial(initial_outages)))
            for Cascade_stage in path.iter('Cascading_Stage'):
                for StageNum in Cascade_stage.iter('Stage_Number'):
                    cascade_outages = list()
                    for outage in StageNum.iter('Outage'):
                        cascade_outages.append(outage.text)
                    self.updateTransitionRelation(self.bdd_transitionRelation.add_expr(self.getTransitionString(initial_outages, cascade_outages)))
                    initial_outages.extend(cascade_outages)
            if self.counter == 300:
                break

        #dumping the bdds in a pickle file
        self.bdd_initiatingEvents.dump('InitiatingEventsExpr.p',[self.initiatingEventExpr])
        self.bdd_transitionRelation.dump('TransitionRelationExpr.p',[self.transitionRelationExpr])

    def printInitiatingEventsBDD(self):
        self.bdd_initiatingEvents.dump('InitiatingEvents.pdf', [self.initiatingEventExpr])

    def printTransitionRelationsBDD(self):
        self.bdd_transitionRelation.dump('TransitionRelation.pdf', [self.transitionRelationExpr])

    def getExpressionStringInitial(self,outage):
        initial_string = ""
        for item in self.vars:
            if item in outage:
                if initial_string:
                    initial_string = initial_string + ' & ' + '!' + item
                else:
                    initial_string = '!' + item
            else:
                if initial_string:
                    initial_string = initial_string + ' & ' + item
                else:
                    initial_string = item
        return initial_string


    def getExpressionStringTransition(self,prevOutage_dict, nextOutage_dict):
        answer1 = ""
        answer2 = ""
        for key in prevOutage_dict:
            if answer1:
                op = " & "
            else:
                op = ""
            if prevOutage_dict[key] :
                answer1 = answer1 + op + key
            else:
                answer1 = answer1 + op + '!' + key
        for key in nextOutage_dict:
            if answer2:
                op = " & "
            else:
                op = ""
            if nextOutage_dict[key] :
                answer2 = answer2 + op + key + 'p'
            else:
                answer2 = answer2 + op + '!' + key + 'p'
        return answer1 + ' & ' + answer2

    def getTransitionString(self, prev, next_):
        prevString = OrderedDict()
        nextString = OrderedDict()
        for var in self.vars:
            prevString[var] = True
            nextString[var] = True
        for item in prev:
            prevString[item] = False
            nextString[item] = False
        for item in next_:
            nextString[item] = False
        return self.getExpressionStringTransition(prevString, nextString)


    def checkInitialState(self, currentState):
        return self.bdd_initiatingEvents.evaluate(self.initiatingEventExpr, currentState)

    def checkSystemState(self, currentState):
        if self.bdd_initiatingEvents.evaluate(self.initiatingEventExpr, currentState) != -1:
            return self.getFixedPointPath(currentState)
        else:
            return False

    def getFixedPointPath(self, currentState):
        path = list();
        initial = self.bdd_transitionRelation.add_expr(self.dictToList(currentState))
        while(self.bdd_transitionRelation.sat_len(initial) != 0):
            temp = _bdd.image(self.transitionRelationExpr, initial, self.primes, self.qvars, self.bdd_transitionRelation)
            path.append(list(self.bdd_transitionRelation.sat_iter(temp)))
            initial = temp
        return path

    def dictToList(self, state):
        answer = ""
        for var in self.vars:
            if answer:
                if state[var]:
                    answer = answer + ' & ' + var
                else:
                    answer = answer + ' & ' + '!' + var
            else:
                if state[var]:
                    answer = var
                else:
                    answer = '!' + var
        return answer
