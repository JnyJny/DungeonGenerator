#!/usr/bin/env python3

import sys
import pygame
from pygame.locals import *
from Dungeon import Dungeon, Room
from StateMachine import State, StateMachine


class GameMode(State):
    def __init__(self,game):
        super(GameMode,self).__init__(type(self).name)
        self.game = game
        self.events = {}
        self.controls = {}
        self.addEvent(QUIT,sys.exit)
        self.addControl(K_ESCAPE,sys.exit)
        self.addControl(K_SPACE,self.handle_spacebar_press)
        self.addControl(K_r,self.reset_requested)
        self.spacebar_pressed = False
        self.reset = False

    def handle_spacebar_press(self):
        self.spacebar_pressed = True

    def reset_requested(self):
        self.reset = True

    def addEvent(self,event,action):
        name = pygame.event.event_name(event)
        self.events.setdefault(name,action)

    def addControl(self,keycode,action):
        self.controls.setdefault(keycode,action)

    def dispatch_pressed(self):
        pressed = pygame.key.get_pressed()
        for key, action in self.controls.items():
            if pressed[key]:
                action()

    def dispatch_events(self):
        for event in pygame.event.get():
            name = pygame.event.event_name(event.type)
            try:
                self.events[name](event)
            except KeyError:
                pass

    def enterAction(self):
        self.spacebar_pressed = False
        self.reset = False
        print('EnterAction:',self.name)

    def exitAction(self):
        print('ExitAction:',self.name)

    def stateAction(self):
        self.dispatch_events()
        self.dispatch_pressed()
        self.game.update()
        self.game.draw()
        pygame.display.update()


class InitializationMode(GameMode):
    name = 'InitializationMode'
    def enterAction(self):
        super(InitializationMode,self).enterAction()
        try:
            del(self.game.dungeon)
        except:
            pass

        self.game.dungeon = Dungeon(self.game.screen.get_width(),
                                    self.game.screen.get_height(),10,10)
        pass
    
    def checkConditions(self):
        if self.reset:
            return InitializationMode.name
        return AddRoomsMode.name
    

class AddRoomsMode(GameMode):
    name = 'AddRoomsMode'
    
    def checkConditions(self):
        if self.reset:
            return InitializationMode.name
        if len(self.game.dungeon.rooms) >= self.game.maxRooms:
            return CollideRoomsMode.name
        
        self.game.dungeon.addRandomRoom(self.game.dungeon.radius/5)

class CollideRoomsMode(GameMode):
    name = 'CollideRoomsMode'

    def stateAction(self):
        self.dispatch_events()
        self.dispatch_pressed()
        self.done = self.game.dungeon.spreadOutRooms(self.game.time,self.screen)
        pygame.display.update()
    
    def enterAction(self):
        super(CollideRoomsMode,self).enterAction()
        self.screen = self.game.screen
    
    def exitAction(self):
        super(CollideRoomsMode,self).exitAction()
        self.game.dungeon.centerIn(self.game.screen.get_rect())
    
    def checkConditions(self):
        if self.reset:
            return InitializationMode.name
        if self.done:
            return IdentifyMainRoomsMode.name
        
class IdentifyMainRoomsMode(GameMode):
    name = 'IdentifyMainRoomsMode'

    def enterAction(self):
        super(IdentifyMainRoomsMode,self).enterAction()
        for room in self.game.dungeon.pickMainRooms(1.25):
            room.render(bgcolor=(255,0,0))

    def checkConditions(self):
        if self.reset:
            return InitializationMode.name
        return FillVoidsMode.name

class FillVoidsMode(GameMode):
    name = 'FillVoidMode'
    def enterAction(self):
        super(FillVoidsMode,self).enterAction()
        self.game.dungeon.inFillWithVoids()


    def checkConditions(self):
        if self.reset:
            return InitializationMode.name
        return MainRoomNeighborsMode.name        

class MainRoomNeighborsMode(GameMode):
    name = 'MainRoomNeighborsMode'

    def stateAction(self):
        self.dispatch_events()
        self.dispatch_pressed()
        self.game.update()
        self.game.draw()

        for room in self.game.dungeon.mainRooms:
            for neighbor in room.neighbors:
                pygame.draw.line(self.game.screen, (0,127,0),
                                 room.rect.center,
                                 neighbor.rect.center,
                                 3)
        pygame.display.update()
        self.elapsed += self.game.time

    
    def enterAction(self):
        super(MainRoomNeighborsMode,self).enterAction()
        self.game.dungeon.findMainRoomNeighbors()
        self.elapsed = self.game.time
    
    def checkConditions(self):
        if self.reset:
            return InitializationMode.name
        
        if self.spacebar_pressed:
            return LocateHallwaysMode.name

        if self.elapsed > 3:
            return LocateHallwaysMode.name


class LocateHallwaysMode(GameMode):
    name = 'LocateHallwayMode'

    def stateAction(self):
        super(LocateHallwaysMode,self).stateAction()

    def enterAction(self):
        super(LocateHallwaysMode,self).enterAction()
        self.game.dungeon.connectHallsToRooms()

    def checkConditions(self):
        if self.reset:
            return InitializationMode.name

    
class Game(StateMachine):

    def __init__(self,gridSpacing=4,frameRate=60):
        super(Game,self).__init__('TheGame.You Lost It.')
        pygame.init()

        self.gridSpacing = gridSpacing
        self.framerate = frameRate
        self.screen = pygame.display.set_mode((1024,1024),0,32)
        pygame.display.set_caption('Procedural Dungeon Generation Demo')
        self.clock = pygame.time.Clock()
        self.maxRooms = 100

        self.add(InitializationMode(self))
        self.add(AddRoomsMode(self))
        self.add(CollideRoomsMode(self))
        self.add(IdentifyMainRoomsMode(self))
        self.add(FillVoidsMode(self))
        self.add(MainRoomNeighborsMode(self))
        self.add(LocateHallwaysMode(self))
        
        self.setStateByName(InitializationMode.name)
        

    @property
    def time(self):
        return self.clock.tick(self.framerate) / 1000.0

    def run(self):
        while True:
            self.think()

    def update(self):
        
        self.dungeon.update(self.time)

    def draw(self):
        
        rects = self.dungeon.draw(self.screen)

        return rects

                
    def quit(self):
        exit()

            
if __name__ == '__main__':
    Game().run()            
