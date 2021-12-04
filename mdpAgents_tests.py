# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent, reconstituteGrid
import api
import random
import game
import util


"""
This class was taken from the modules page solution for practical 5 https://keats.kcl.ac.uk/course/view.php?id=93374 . All methods in the MDPAgent class taken from this practical solution
will be marked with a line of * symbols
"""
#
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
#
class Grid:
         
    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],

            # A new line after each line of the grid
            print 
        # A line after the grid
        print
    

        
    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width




class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

        # Create lists to manage better the current state info
        self.restartLists()

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)

        self.makeMap(state)
        self.addWallsToMap(state)
        self.updateFoodInMap(state)
        self.mapWidth = self.getLayoutWidth(api.corners(state))
        self.mapHeight = self.getLayoutHeight(api.corners(state))

    # Sets the info lists to empty to both start and restart the game
    def restartLists(self):
        self.visited = []
        self.walls = []
        self.capsules = []
        self.food = []

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
        self.restartLists()

    
    def getAction(self, state):
        self.food = api.food(state)
        self.walls = api.walls(state)
        self.capsules = api.capsules(state)
        self.corners = api.corners(state)
        self.ghosts = [tuple(map(int, x)) for x in api.ghosts(state)]
        self.ghostStates = api.ghostStatesWithTimes(state)
        self.timeToEat = dict.fromkeys(self.ghosts, False)
        for t in self.timeToEat.keys():
            for s in self.ghostStates:
                if s[0] == t:
                    self.timeToEat[t] = s[1] >=2
        
        print (self.timeToEat)
        # print("GHOSTS", self.ghosts)
        
        
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        # Set the utility values in the map
        utilityMap = self.setUtilities(state)

        bigMap = self.mapWidth >= 10 and self.mapHeight >= 10

        # Run value iteration
        self.valueIteration(state, 0.1, 0.7, 300, utilityMap, bigMap)

        for i in range(self.mapWidth):
            for j in range(self.mapHeight):
                if self.map.getValue(i,j):
                    self.map.setValue(i,j, utilityMap[(i,j)])
        
        policy = self.policy(state, utilityMap)
        print(api.whereAmI(state))
        print(policy)
        self.map.prettyDisplay()
        # self.locationsDisplay()
        return api.makeMove(policy, legal)


    def locationsDisplay(self):       
        for i in range(self.mapHeight):
            for j in range(self.mapWidth):
                # print grid elements with no newline
                if (i,j) in self.walls:
                    print "%",
                else:
                    print "({}, {})".format(i,j),

            # A new line after each line of the grid
            print 
        # A line after the grid
        print
    """
    **********************************************************************
    """
    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)
        

    def setUtilities(self, state):
        # First store the currents state info in variables
        pacman = api.whereAmI(state)

        # Then record the information of the current state in the previously created lists
        if pacman not in self.visited:
            self.visited.append(pacman)

        # Create a reward map to store the value at each location from the information recorded
        utilityMap = {}
        utilityMap.update(dict.fromkeys(self.food, 2.0))
        utilityMap.update(dict.fromkeys(self.capsules, 2.0))
        utilityMap.update(dict.fromkeys(self.walls, "%"))

        # Temp map to check for convergence
        self.tempMap = {}
        self.tempMap.update(dict.fromkeys(self.food, 0.0))
        self.tempMap.update(dict.fromkeys(self.capsules, 0.0))
        self.tempMap.update(dict.fromkeys(self.walls, "%"))


        # Update visited and ghost values
        self.updateVisited(utilityMap)
        self.updateGhosts(state, utilityMap)

        return utilityMap

    # Calculate the utility of each possible action
    def getUtilities(self, location, utilityMap):
        # Store utilities in dicitionary to make it easier
        self.utilities = {"North":0.0, "South": 0.0, "East": 0.0, "West":0.0}
        # We store the reward map as a class variable
        self.utilityMap = utilityMap

        # Create variables for each possible location
        north = (location[0], location[1]+1)
        south = (location[0], location[1]-1)
        east = (location[0]+1, location[1])
        west = (location[0]-1, location[1])

        # Now calculate all utilities
        # First check if the location is a wall 
        # If its a wall we add the utility value of staying on the current location

        # NORTH
        if self.utilityMap[north] != "%":
            self.utilities["North"] += 0.8 *self.utilityMap[north]
        else: 
            # print(self.utilityMap[location])
            self.utilities["North"] += 0.8 *self.utilityMap[location]
        
        if self.utilityMap[east]!= "%":
            self.utilities["North"] += 0.1 *self.utilityMap[east]
        else: 
            self.utilities["North"] += 0.1 *self.utilityMap[location]
        
        if self.utilityMap[west]!= "%":
            self.utilities["North"] += 0.1 *self.utilityMap[west]
        else: 
            self.utilities["North"] += 0.1 *self.utilityMap[location]

        
        # SOUTH
        if self.utilityMap[south]!= "%":
            self.utilities["South"] += 0.8 *self.utilityMap[south]
        else: 
            self.utilities["South"] += 0.8 *self.utilityMap[location]
        
        if self.utilityMap[east]!= "%":
            self.utilities["South"] += 0.1 *self.utilityMap[east]
        else: 
            self.utilities["South"] += 0.1 *self.utilityMap[location]
        
        if self.utilityMap[west]!= "%":
            self.utilities["South"] += 0.1 *self.utilityMap[west]
        else: 
            self.utilities["South"] += 0.1 *self.utilityMap[location]
        
        # EAST
        if self.utilityMap[east]!= "%":
            self.utilities["East"] += 0.8 *self.utilityMap[east]
        else: 
            self.utilities["East"] += 0.8 *self.utilityMap[location]
        
        if self.utilityMap[north]!= "%":
            self.utilities["East"] += 0.1 *self.utilityMap[north]
        else: 
            self.utilities["East"] += 0.1 *self.utilityMap[location]
        
        if self.utilityMap[south]!= "%":
            self.utilities["East"] += 0.1 *self.utilityMap[south]
        else: 
            self.utilities["East"] += 0.1 *self.utilityMap[location]
        
        # WEST
        if self.utilityMap[west]!= "%":
            self.utilities["West"] += 0.8 *self.utilityMap[west]
        else: 
            self.utilities["West"] += 0.8 *self.utilityMap[location]
        
        if self.utilityMap[north]!= "%":
            self.utilities["West"] += 0.1 *self.utilityMap[north]
        else: 
            self.utilities["West"] += 0.1 *self.utilityMap[location]
        
        if self.utilityMap[south]!= "%":
            self.utilities["West"] += 0.1 *self.utilityMap[south]
        else: 
            self.utilities["West"] += 0.1 *self.utilityMap[location]
        
        return self.utilities


    # Get the maximum expected utility for a location and update the reward map with that value
    def transitionModel(self, location, utilityMap):
        self.getUtilities(location, utilityMap)
        self.utilityMap[location] = max(self.utilities.values())

        return self.utilityMap[location]


    def valueIteration(self, state, reward, discount, iterations, utilityMap, bigMap):
        foodReward = 2.0
        nearGhostReward = -10.0
        nearGhostScared = 5.0
        ghostReward = -20.0
        ghostScared = 7.0
        capsuleReward = 5.0


        nearGhosts = []
        for g in self.ghosts:
            if bigMap:
                for n in self.squareNeighbours(g):
                    nearGhosts.append(n)
            else:
                for n in self.oneDistNeighbours(g):
                    nearGhosts.append(n)
                
        # print("NEAR GHOST LOCATIONS", nearGhosts)
        


        while iterations > 0:
            # Copy old map. This is done because if we update the values on the same map, the new values will alter the result of the next ones
            old = utilityMap.copy()
           
            # Iterate locations
            for i in range(self.mapWidth-1):
                for j in range(self.mapHeight-1):
                    # if self.emptyLoc((i,j)):
                    #         # Set

                    if not (i,j) in self.walls:
                        # EMPTY LOCATION
                        if (i,j) not in self.food and not (i,j) in self.capsules and not (i,j) in self.ghosts and not (i,j) in nearGhosts:
                            utilityMap[(i,j)] = round(reward + discount * self.transitionModel((i,j), old),2)
                        # FOOD LOCATION
                        elif (i,j) in self.food and not (i,j) in self.capsules and not (i,j) in self.ghosts and not (i,j) in nearGhosts:
                            utilityMap[(i,j)] = round(foodReward + discount * self.transitionModel((i,j), old),2)
                        # GHOST LOCATION
                        elif (i,j) in self.ghosts:  
                            if not self.timeToEat[(i,j)]:     
                                utilityMap[(i,j)] = round(ghostReward + discount * self.transitionModel((i,j), old),2)
                            else:
                                utilityMap[(i,j)] = round(ghostScared + discount * self.transitionModel((i,j), old),2)


                        # CAPSULE LOCATION
                        elif (i,j) in self.capsules and not (i,j) in self.ghosts and not (i,j) in nearGhosts and not (i,j) in self.food:
                            utilityMap[(i,j)] = round(capsuleReward + discount * self.transitionModel((i,j), old),2)
                        
                        elif (i,j) in nearGhosts:
                            # if not self.timeToEat:
                            utilityMap[(i,j)] = round(nearGhostReward + discount * self.transitionModel((i,j), old),2)
                            # else:
                            #     utilityMap[(i,j)] = round(nearGhostScared + discount * self.transitionModel((i,j), old),2)

                

                            

                    

            iterations -=1

    # Returns the policy for pacmans location. 
    # Takes a map previously iterated with the valueIteration method
    def policy(self, state, utilityMap):

        pacman = api.whereAmI(state)

        # Assign utilityMap class variable to parameter
        self.utilityMap = utilityMap
        
        # Get utilities for the current location
        self.getUtilities(pacman, self.utilityMap)
        MEU = max(self.utilities.values())

        return self.utilities.keys()[self.utilities.values().index(MEU)]

    def oneDistNeighbours(self, location):
        locX = location[0]
        locY = location[1]
        neighbours = []
        
        if not (locX+1, locY) in neighbours and not (locX+1, locY) in self.walls and not self.outOfbounds((locX+1, locY), self.corners):
            neighbours.append((locX+1, locY))
        if not (locX-1, locY) in neighbours and not (locX-1, locY)  in self.walls and not self.outOfbounds((locX-1, locY) , self.corners):
            neighbours.append((locX-1, locY))
        if not (locX, locY+1) in neighbours and not (locX, locY+1) in self.walls and not self.outOfbounds((locX, locY+1), self.corners):
            neighbours.append((locX, locY+1))
        if not (locX, locY-1) in neighbours and not (locX, locY-1)in self.walls and not self.outOfbounds((locX, locY-1), self.corners):
            neighbours.append((locX, locY-1))

        return neighbours


    def squareNeighbours(self, location):
        locX = location[0]
        locY = location[1]
        neighbours = []
        
        for i in range (locX-1, locX+2):
            for j in range(locY-1, locY+2):
                if not (i,j) in self.walls and not self.outOfbounds((i,j), self.corners) and not (i,j) == location:
                    neighbours.append((i,j))

        return neighbours


    # Make square not cross of coordinates
    def FiveDistNeighbours(self, location):
        locX = location[0]
        locY = location[1]
        neighbours = []
        
        for i in range(1, 3):
            if not (locX+i, locY) in neighbours and not (locX+i, locY) in self.walls and not self.outOfbounds((locX+i, locY), self.corners):
                neighbours.append((locX+i, locY))
            if not (locX-i, locY) in neighbours and not (locX-i, locY)  in self.walls and not self.outOfbounds((locX-i, locY) , self.corners):
                neighbours.append((locX-i, locY))
            if not (locX, locY+i) in neighbours and not (locX, locY+i) in self.walls and not self.outOfbounds((locX, locY+i), self.corners):
                neighbours.append((locX, locY+i))
            if not (locX, locY-i) in neighbours and not (locX, locY-i)in self.walls and not self.outOfbounds((locX, locY-i), self.corners):
                neighbours.append((locX, locY-i))
        return neighbours


    def outOfbounds(self, loc, corners):
        mapWidth = self.getLayoutWidth(self.corners)
        mapHeight = self.getLayoutHeight(self.corners)
        if loc[0] > self.mapWidth or loc[1] > self.mapHeight:
            return True
        return False

    # Check if its an empty location
    def emptyLoc(self, location):
        if location not in self.walls:
            return True
        return False



    def updateGhosts(self, state, utilityMap):
        ghostStates = api.ghostStates(state)

        for loc in utilityMap.keys():
            for i in range(len(self.ghosts)):
 
                # api stores locations as float so we have to cast
                ghostLoc = ((int(self.ghosts[i][0])), (int(self.ghosts[i][1])))
            
                if ghostLoc == loc:
                    utilityMap[loc] = -10


    # Updates values of utilityMap to mark visited locations with value 0
    def updateVisited(self,utilityMap):
        # First mark pacman initial position as visited
        for i in range(self.mapWidth):
            for j in range(self.mapHeight):
                if (i, j) not in utilityMap.keys():
                    utilityMap[(i, j)] = 0.0
                
        # Update food and capsules eaten too
        for f in self.food:
            if f in self.visited:
                utilityMap[f] = 0.0

        for c in self.capsules:
            if c in self.visited:
                utilityMap[c] = 0.0



    """
    **********************************************************************
    """
    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1
    
    """
    **********************************************************************
    """
    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1
    
    """
    **********************************************************************
    """
    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(self.walls)):
            self.map.setValue(self.walls[i][0], self.walls[i][1], '%')
    
    """
    **********************************************************************
    """
    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, ' ')
        food = api.food(state)
        for i in range(len(self.food)):
            self.map.setValue(self.food[i][0], self.food[i][1], '*')





# #! CHANGE
                    # if(bigMap):
                    #     for g in self.ghosts:
                    #         if ((i,j) in self.FiveDistNeighbours(g, self.food) ):
                    #             utilityMap[(i,j)] = reward + discount * self.transitionModel((i,j), old)
                                
                    # else:
                    #     if self.emptyLoc((i,j), self.food, self.walls, self.ghosts, capsules):
                    #         # Set
                    #         utilityMap[(i,j)] = reward + discount * self.transitionModel((i,j), old)