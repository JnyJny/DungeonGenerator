#!/usr/bin/env python3

import math
import random
import pygame
import pygame.color




def roundm(n,m):
    rnd = lambda x: math.floor((x+m-1)/m)*m
    try:
        return [x for x in rnd(n)]
    except TypeError:
        return rnd(n)

def slope(p0,p1):
    try:
        m = (p1[1] - p0[1]) / (p1[0] - p0[0])
    except ZeroDivisionError:        
        m = 0
    return m

def collide_rooms(left,right):
    
    if left == right:           # ignore self collisions
        return False
    
    left_shrunk = left.rect.inflate(-2,-2)
    right_shrunk = right.rect.inflate(-2,-2)

#    left_shrunk.center = left.rect.center
#    right_shrunk.center = right.rect.center
    
    return right_shrunk.colliderect(left_shrunk)

def collide_and_scatter_rooms(left,right):
    
    if collide_rooms(left,right):
        right.repulse(left)
        return True
    right.velocity *= 0
    return False

def gridToScreen(count,spacing):
    return ((spacing+1)*count)+1

def screenToGrid(coord,spacing):
    return roundm(coord/(spacing+1),spacing)

def collide_with_voids(left,right):
    return right.isVoid and collide_rooms(left,right)

def snap_rect_to_grid(rect,gridSpacing):
    grid = gridSpacing+1
    rect.x = roundm(rect.x,grid)
    rect.y = roundm(rect.y,grid)
    rect.w = roundm(rect.w,grid)
    rect.h = roundm(rect.h,grid)

class Room(pygame.sprite.Sprite):
    _id = 0
    @classmethod
    def fromRect(cls,rect,gridSpacing):
        r = Room(gridSpacing=gridSpacing)
        r.rect = rect
        return r

    @classmethod
    def nextID(cls):
        i = cls._id
        cls._id += 1



    def __init__(self,x=0,y=0,width=1,height=1,gridSpacing=1):
        '''
                 x, y : dungeon surface coords
        width, height : in grid units
          gridSpacing : interior diameter of grid unit
        '''
        super(Room,self).__init__()

        self.id = Room.nextID()
        
        self.width       = width
        self.height      = height        
        self.gridSpacing = gridSpacing
        
        self.velocity = pygame.math.Vector2(0,0)

        self.image = pygame.Surface((gridToScreen(width,gridSpacing),
                                     gridToScreen(height,gridSpacing)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.neighbors = []
        self.snapToGrid()
        self.render()

    def __repr__(self):
        return 'Room(%d,%s,velocity=%s)' % (self.id,self.rect,self.velocity)

    @property
    def fgcolor(self):
        return Dungeon.COLORS[self.layer][0]

    @property
    def bgcolor(self):
        return Dungeon.COLORS[self.layer][1]

    @property
    def layer(self):
        try:
            return self._layer
        except AttributeError:
            self._layer = Dungeon.VOIDS
        return self._layer

    @layer.setter
    def layer(self,newLayer):
        self._layer = newLayer

    @property
    def vector(self):
        try:
            return self._vector
        except AttributeError:
            self._vector = pygame.math.Vector2(self.rect.center)
        return self._vector

    @property
    def isVoid(self):
        return self.layer == Dungeon.VOIDS

    @property
    def isHall(self):
        return self.layer == Dungeon.HALLS

    @property
    def isMainRoom(self):
        return self.layer == Dungeon.MAIN_ROOMS

    def centerbox(self,other):
        x = min(self.rect.x,other.rect.x)
        y = min(self.rect.y,other.rect.y)
        w = max(self.rect.x,other.rect.x) - x
        h = max(self.rect.y,other.rect.y) - y
        return pygame.rect.Rect(x,y,w,h)

    
    def distance_to(self,other):
        return self.vector.distance_to(other.vector)

    def containsX(self,x,smidge=3):
        return (self.rect.topleft[0] <= x) and (self.rect.topright[0] >= x)
    
    def containsY(self,y,smidge=3):
        return (self.rect.topleft[1] <= y) and (self.rect.bottomleft[1] >= y)

    def snapToGrid(self,grid=None):
        if grid is None:
            grid = self.gridSpacing+1
        self.rect.x = roundm(self.rect.x,grid)
        self.rect.y = roundm(self.rect.y,grid)

    def _goodNeighbor(self,other):
        if (self == other):
            return False
        if self.neighbors.count(other) != 0:
            return False
        return True

    def pickClosestNeighbors(self,potentials,limit,reset=False):
        '''
        potentials: list of Rooms
             limit: integer specifying upper limit of rooms to pick as neighbors
             reset: clear out neighbors list before finding more neighbors
        '''
        if reset:
            self.neighbors = []

        # build a neighborhood dictionary keyed on distance between
        # the target room and the potential neighbors. skip rooms
        # that aren't good neighbors.
        
        neighborhood = {}
        for p in potentials:
            if self._goodNeighbor(p):
                neighborhood.setdefault(self.distance_to(p),p)

        newNeighbors = [neighborhood[d] for d in sorted(neighborhood)][:limit]

        self.neighbors.extend(newNeighbors)
        
        return self.neighbors

    def update(self,time):
        self.move(time)
        self.snapToGrid()

    def move(self,time):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

    def repulse(self,other):
        dx = (self.rect.x - other.rect.x)
        dy = (self.rect.y - other.rect.y)
        self.velocity.x += dx + random.randint(-10,10) * random.randint(-1,1)
        self.velocity.y += dy + random.randint(-10,10) * random.randint(-1,1)

    def render(self,fgcolor=None,bgcolor=None,width=1):

        if fgcolor is None:
            fgcolor = self.fgcolor
            
        if bgcolor is None:
            bgcolor = self.bgcolor
            
        self.image.fill(bgcolor)

        grid = pygame.rect.Rect(0,0,self.gridSpacing+2,self.rect.height)
        
        for grid.x in range(0,self.rect.width,(self.gridSpacing+1)*2):
            pygame.draw.rect(self.image,fgcolor,grid,width)

        grid = pygame.rect.Rect(0,0,self.rect.width,self.gridSpacing+2)
        for grid.y in range(0,self.rect.height,(self.gridSpacing+1)*2):
            pygame.draw.rect(self.image,fgcolor,grid,width)

        pygame.draw.rect(self.image,fgcolor,grid,width)


class Dungeon(pygame.sprite.RenderUpdates):
    VOIDS = 0
    HALLS = 5
    MAIN_ROOMS=10
    COLORS = { VOIDS:     ((127,127,127),(0,0,0)), # fg,bg
               HALLS:     ((255,255,255),(0,0,255)),
               MAIN_ROOMS:((255,255,255),(255,0,0))}

    @classmethod
    def generate(cls,width,height,maxRoomDimension=10,gridSpacing=8,seedRooms=150):

        dungeon = cls(width,height,
                      maxRoomDimension,
                      maxRoomDimension,
                      gridSpacing)

        for x in range(0,seedRooms):
            dungeon.addRandomRoom(dungeon.radius/5) # XXX magic number

        dungeon.spreadOutRooms()

        dungeon.centerIn(pygame.rect.Rect(0,0,dungeon.width,dungeon.height))

        for room in dungeon.pickMainRooms(1.25): # XXX magic number
            dungeon.setRoomType(room,Dungeon.MAIN_ROOMS)
            
        dungeon.inFillWithVoids()

        dungeon.findMainRoomNeighbors()

        dungeon.connectHallsToRooms()

        return dungeon
        
    
    def __init__(self,width,height,maxRoomWidth,maxRoomHeight,gridSpacing=8):
        '''
        width, height : pixels
        maxRoomWidth  : grid units
        maxRoomHeight : grid units
        gridSpacing   : grid void distance
        '''
        self.width = width
        self.height = height
        self.gridSpacing = gridSpacing
        self.rooms = pygame.sprite.LayeredUpdates()

        self.bgcolor = (80,80,80)
        self.maxWidth = maxRoomWidth
        self.maxHeight = maxRoomHeight
        self.rect = pygame.rect.Rect(0,0,self.width,self.height)

    @property
    def font(self):
        try:
            return self._font
        except AttributeError:
            pygame.sysfont.initsysfonts()
            self._font = pygame.sysfont.SysFont(None,14)
        return self._font

    @property
    def bound(self):
        rooms = self.rooms.sprites()
        if len(rooms):
            u = rooms[0].rect.unionall([r.rect for r in rooms[1:]])
        else:
            u = None
        return u

    @property
    def radius(self):
        return min(self.width,self.height) / 2

    @property
    def mainRooms(self):
        return self.rooms.get_sprites_from_layer(self.MAIN_ROOMS)

    @property
    def halls(self):
        return self.rooms.get_sprites_from_layer(self.HALLS)

    @property
    def voids(self):
        return self.rooms.get_sprites_from_layer(self.VOIDS)

    def setRoomType(self,room,layer,render=True):
        self.rooms.change_layer(room,layer)
        room.layer = layer
        if render:
            room.render()

    def centerIn(self,rect):
        dx = rect.center[0] - self.bound.center[0]
        dy = rect.center[1] - self.bound.center[1]
        for room in self.rooms.sprites():
            room.rect.x += dx
            room.rect.y += dy

    def addRandomRoom(self,radius=None):

        if radius is None:
            radius = self.radius
        
        w = random.randint(1,self.maxWidth)
        h = random.randint(1,self.maxHeight)
        t = 2.0 * math.pi * random.random()
        u = random.random() + random.random()
        if u > 1:
            r = 2 - u
        else:
            r = u
        x = radius * r * math.cos(t) + self.rect.center[0]
        y = radius * r * math.sin(t) + self.rect.center[1]

        self.rooms.add(Room(x,y,w,h,self.gridSpacing),layer=self.VOIDS)

    def pickMainRooms(self,pickRatio):

        rooms = self.rooms.sprites()
        nrooms = len(rooms)

        pick_w = pickRatio * (sum([r.rect.w for r in rooms]) / nrooms)
        pick_h = pickRatio * (sum([r.rect.h for r in rooms]) / nrooms)

        for room in rooms:
            if room.rect.width < pick_w or room.rect.height < pick_h:
                self.setRoomType(room,Dungeon.VOIDS)
                continue
            self.setRoomType(room,Dungeon.MAIN_ROOMS)
                    
        return self.mainRooms

    def findMainRoomNeighbors(self,maxEdges=2):
        rooms = self.mainRooms
        for room in rooms:
            room.pickClosestNeighbors(rooms,maxEdges)
    
    def connectHallsToRooms(self,hallwidth=3):

        w =  gridToScreen(hallwidth,self.gridSpacing)
        
        for room in self.mainRooms:
            for neighbor in room.neighbors:

                target = room.centerbox(neighbor)

                collider = Room.fromRect(target.inflate(w,w),self.gridSpacing)
                collider.snapToGrid()

                outers = pygame.sprite.spritecollide(collider,self.rooms,False,
                                                     collide_with_voids)

                collider = Room.fromRect(target.inflate(-w,-w),self.gridSpacing)
                collider.snapToGrid()

                inners = pygame.sprite.spritecollide(collider,self.rooms,False,
                                                     collide_with_voids)

                for v in outers:
                    if v in inners and (v.width == 1) and (v.height == 1):
                        continue
                    self.setRoomType(v,Dungeon.HALLS)
                    v.render()


    def inFillWithVoids(self,width=1,height=1,bounds=None):

        if bounds is None:
            bounds = self.bound

        voids = pygame.sprite.Group()
        xfin = bounds.x + bounds.width - (self.gridSpacing+1)
        yfin = bounds.y + bounds.height - (self.gridSpacing+1)

        for x in range(bounds.x,xfin,self.gridSpacing+1):
            for y in range(bounds.y,yfin,self.gridSpacing+1):
                r = Room(x,y,gridSpacing=self.gridSpacing)
                voids.add(r)

        pygame.sprite.groupcollide(voids,self.rooms,True,False,collide_rooms)

        self.rooms.add(voids,layer=Dungeon.VOIDS)

    def stopRooms(self):
        for room in self.rooms.sprites():
            room.velocity *= 0
            room.snapToGrid()        

    def spreadOutRooms(self,time=0,surface=None):

        done = False
        rooms = self.rooms.sprites()

        while not done:
            self.rooms.update(time)
            done = True
            for room in rooms:
                room.render()
                collisions = pygame.sprite.spritecollide(room,rooms,False,
                                                         collide_and_scatter_rooms)
                if len(collisions):
                    if surface:
                        room.render(bgcolor=(255,0,0))
                    done = False
                    break

            if surface and not done:
                self.draw(surface,True)
                return False

        self.stopRooms()
        return True
            

    def update(self,time):
        self.rooms.update(time)
        
    def draw(self,surface,drawBounds=True):
    
        surface.fill(self.bgcolor)

        rects = self.rooms.draw(surface)

        if drawBounds:
            try:
                pygame.draw.rect(surface,(0,128,0,0.1),self.bound.inflate(2,2),1)
            except:
                pass


        return rects


if __name__ == '__main__':

    from pygame.locals import *

    pygame.init()

    screen_size = (1024,1024)
    
    screen = pygame.display.set_mode(screen_size,0,32)
    
    pygame.display.set_caption('Dungeon Generation Demo')
    
    dungeon = Dungeon.generate(screen_size[0],screen_size[1])

    while True:
        dungeon.update(0)
        dungeon.draw(screen)
        pygame.display.update()
        pressed = pygame.key.get_pressed()
        if pressed[K_ESCAPE]:
            exit()        

