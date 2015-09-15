#!/usr/bin/env python

class State(object):
    def __init__(self,name):
        self.name = name

    def stateAction(self):
        pass

    def checkConditions(self):
        pass

    def enterAction(self):
        pass
    
    def exitAction(self):
        pass

class StateMachine(dict):
    def __init__(self,name):
        self.name = name
        self.currentState = None

    def add(self,state):
        self.setdefault(state.name,state)

    def setStateByName(self,stateName,doExitAction=True,doEnterAction=True):
        
        if self.currentState is not None and doExitAction:
            self.currentState.exitAction()
            
        self.currentState = self[stateName]
        
        if doEnterAction:
            self.currentState.enterAction()

    def think(self):
        if self.currentState is None:
            return

        self.currentState.stateAction()

        newStateName = self.currentState.checkConditions()
        
        if newStateName is not None:
            self.setStateByName(newStateName)
    
    
