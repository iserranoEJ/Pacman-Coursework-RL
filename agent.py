import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from util import Queue

class Agent(object):
    def __init__(self, name, colour, node):
        self.name = name
        self.node = node
        self.setPosition()
        self.directions = {STOP:Vector2(), UP:Vector2(0,-1), DOWN:Vector2(0,1), LEFT:Vector2(-1,0), RIGHT:Vector2(1,0)}
        self.direction = STOP
        self.speed = 100
        self.radius = 10
        self.colour = colour
        self.trail = self.Trail(self.colour, self.position)
        
        
        self.target = node
        self.collideRadius = 5


    def setPosition(self):
        self.position = self.node.position.copy()

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            d = self.position - pellet.position
            dSquared = d.magnitudeSquared()
            rSquared = (pellet.radius+self.collideRadius)**2
            if dSquared <= rSquared:
                return pellet
        return None
    
    def isEating(self, pelletList):
        for pellet in pelletList:
            d = self.position - pellet.position
            dSquared = d.magnitudeSquared()
            rSquared = (pellet.radius+self.collideRadius)**2
            if dSquared <= rSquared:
                return True
        return False

    def update(self, dt, pelletList):	
        self.position += self.directions[self.direction]*self.speed*dt
        direction = self.getValidKey()

        if self.isEating(pelletList):
            self.trail.updateEating(self.position)
        else:
            self.trail.update(self.position)

        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else: 
            if self.oppositeDirection(direction):
                self.reverseDirection()


    def reverseDirection(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def oppositeDirection(self, direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def validDirection(self, direction):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                return True
        return False

    def getNewTarget(self, direction):
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node



    def overshotTarget(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False 

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def render(self, screen):
        p = self.position.asInt()
        self.trail.render(screen)
        pygame.draw.circle(screen, self.colour, p, self.radius)
    
    
    class Trail:
        def __init__(self, colour, position):
            self.queue = Queue()
            self.queue.push(position)
            self.length = self.queue.size()
            self.colour = colour
        
        def update(self, position):
            self.queue.pop()
            self.queue.push(position)

        def updateEating(self, position):
            self.queue.push(position)
        
        def render(self, screen):
            for el in self.queue.list:
                pygame.draw.rect(screen, self.colour, (el.asInt()[0]- 5,el.asInt()[1] - 5, 10,10), border_radius = 5)

