from numpy.lib.function_base import percentile
import pygame
from vector import Vector2
from constants import *
import numpy as np
import random

class Pellet(object):
    def __init__(self, row, column):
        self.name = PELLET
        self.position = Vector2(column*TILEWIDTH, row*TILEHEIGHT)
        self.color = WHITE
        self.radius = int(4 * TILEWIDTH / 16)
        self.collideRadius = int(4 * TILEWIDTH / 16)
        self.points = 10
        self.visible = True
        
    def render(self, screen):
        if self.visible:
            p = self.position.asInt()
            pygame.draw.circle(screen, self.color, p, self.radius)
 

class PowerPellet(Pellet):
    def __init__(self, row, column):
        Pellet.__init__(self, row, column)
        self.name = POWERPELLET
        self.radius = int(8 * TILEWIDTH / 16)
        self.points = 50
        self.flashTime = 0.2
        self.timer= 0
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.flashTime:
            self.visible = not self.visible
            self.timer = 0

class PelletGroup(object):
    def __init__(self, pelletfile):
        self.pelletList = []
        self.powerpellets = []
        self.data = self.readPelletfile(pelletfile)
        self.createPelletList()
        self.numEaten = 0
        

    def update(self, dt):
        for powerpellet in self.powerpellets:
            powerpellet.update(dt)

        #!#############################
        self.randomPelletGenerator()

    #!
    def randomPelletGenerator(self):
        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1]):
                if self.data[row][col] in ['.', '+']:
                    rand = random.randint(0,1000)
                    # Have a 1/1000 chance to make a pellet appear on screen
                    if rand == 1:
                        pel =  Pellet(row, col)
                        if not pel in self.pelletList:
                            self.pelletList.append(pel)
                elif self.data[row][col] in ['P', 'p']:
                    rand2 = random.randint(0,4000)
                    # Have a 1/4000 chance to make a pellet appear on screen
                    if rand2 == 1:
                        pp = PowerPellet(row, col)
                        if not pp in self.powerpellets:
                            self.pelletList.append(pp)
                            self.powerpellets.append(pp)
                
    def createPelletList(self):
        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1]):
                if self.data[row][col] in ['.', '+']:
                    self.pelletList.append(Pellet(row, col))
                elif self.data[row][col] in ['P', 'p']:
                    pp = PowerPellet(row, col)
                    self.pelletList.append(pp)
                    self.powerpellets.append(pp)
                    
    def readPelletfile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')
    
    def isEmpty(self):
        if len(self.pelletList) == 0:
            return True
        return False
    
    def render(self, screen):
        for pellet in self.pelletList:
            pellet.render(screen)
