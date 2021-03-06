# myTeam.py
# ---------
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

# Importing necessary libraries
from captureAgents import CaptureAgent
import random, time, util, sys
import math
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'NorthAgent', second = 'SouthAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    '''
    init code is below
    '''
    # This is used to count turns that we are waiting
    self.counter = 0
    # States to determines what the agent is doing
    self.inHiding = False
    self.doneHiding = False
    self.attacking = False
    self.defending = False
    # Holds the coordinates for where we'll hide
    self.hidingSpot = (0, 0)
    self.hidingSpotList = [0, 0]
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def findNearestFood(self, gameState):
    """
    Finds and returns the nearest food from the agent
    """
    nearestFoodDistance = 9999
    nearestFood = (1,1)
    for food in self.getFood(gameState).asList():
      dist = self.getMazeDistance(gameState.getAgentPosition(self.index),food)   
      if dist < nearestFoodDistance:
        nearestFoodDistance = dist
        nearestFood = food
    return nearestFood

  def findPath(self, gameState, position):
    """
    Returns the action that gets us closer to the given position 
    This also flags paths with an enemy ghost on them. 
    """
    bestDist = 9999
    enemyOnPath = False
    actions = gameState.getLegalActions(self.index)
    for action in actions:
      successor = self.getSuccessor(gameState, action)
      pos2 = successor.getAgentPosition(self.index)
      if not enemyOnPath: # used to flag if we should go this way
        enemyAgents = []
        if self.getColor(gameState) == "Red": # code to get enemy agents
          enemyAgents = gameState.getBlueTeamIndices()
        else:
          enemyAgents = gameState.getRedTeamIndices()
        for agent in enemyAgents: # checking if enemy agents are on our suggested path
          if gameState.getAgentPosition(agent) == pos2 and gameState.getAgentState(agent).scaredTimer <= 0:
            enemyOnPath = True 
      dist = self.getMazeDistance(position,pos2)
      if dist < bestDist:
        bestAction = action
        bestDist = dist
    if enemyOnPath:
      return (bestAction, 1) # returns the best action AND a 1 if an enemy is on the path
    else:
      return (bestAction, 0) # returns the best action AND a 0 if an enemy is on the path

  def getSuccessor(self, gameState, action):
    """
    Get potential successors, used to help determine a move
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def getColor(self, gameState):
    """
    Determine which color team is
    This is used for determining hiding location, finding power capsules, etc
    """
    if self.red == True:
      return "Red"
    else:
      return "Blue"

  def getFeatures(self, gameState, action):
    """
    Determine a list of features, this will help us determine which action to take
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
		
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
		
    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)
	
    # Compute distance and location for the nearest food
    if len(foodList) > 0: 
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = 9999
      closestFood = [0, 0]
      for food in foodList:
        if minDistance > self.getMazeDistance(myPos, food):
          minDistance = self.getMazeDistance(myPos, food)
          closestFood = food
      closeFood = tuple(closestFood)
      features['distanceToFood'] = minDistance
      features['closeFood'] = closeFood
    return features

  def foodCollection(self, gameState):
    """
    This method contains logic for attacking, collecting food, collecting
    capsules, and returning to our side of the map.
    """
    actions = gameState.getLegalActions(self.index)
    foodLeft = len(self.getFood(gameState).asList())
    features = [self.getFeatures(gameState, a) for a in actions]

    capPos = None
    if self.getColor(gameState) == "Red":
      capPos = gameState.getBlueCapsules()
    else:
      capPos = gameState.getRedCapsules()

    # Food Collecting
    if self.attacking == True and gameState.getAgentState(self.index).numCarrying < 9 and foodLeft > 2:
      bestActions = []
      closeFoodPos = []
      tempPos = []
      for dct in features:
        for k, v in dct.items():
          if k == 'closeFood':
            tempPos.append(dct['closeFood'])
          if k == 'distanceToFood':
            bestActions.append(v)
      
      minVal = min(bestActions)
      i = bestActions.index(minVal)
      closeFoodPos = tuple(tempPos[i])

      # Searching for capsule if carrying some food
      if gameState.getAgentState(self.index).numCarrying >= 6 and len(capPos) != 0:
        return self.findPath(gameState, capPos[0])[0]
      else:
        return self.findPath(gameState, closeFoodPos)[0]

    # Return to start if carrying a large amount of food
    # Attempt to juke incoming defenders
    else:
      if self.findPath(gameState, self.start)[1] != 1:
        return self.findPath(gameState, self.start)[0]
      elif len(capPos) != 0:
        if self.findPath(gameState, capPos[0])[1] != 1:
          return self.findPath(gameState, capPos[0])[0]
      else:
        return random.choice(actions)

class NorthAgent(DummyAgent):
  """
  This agent hides on the north side of the map.
  """
  def chooseAction(self, gameState):

    # Determine whether we're in hiding place
    if self.hidingSpot[0] == gameState.getAgentPosition(self.index)[0] and self.hidingSpot[1] == gameState.getAgentPosition(self.index)[1]:
      self.inHiding = True
      self.doneHiding = True
      self.attacking = True
    if self.inHiding == True:
      turnsToWait = 6
      # Leave hiding spot after number of turns
      if self.counter == turnsToWait:
        self.inHiding = False
      # increment counter and return stop action
      else:
        self.counter += 1
        return 'Stop'

    # Get hiding location and go there
    if self.inHiding == False and self.doneHiding == False:
      if self.getColor(gameState) == "Red": # Red team
        # X is 14 and Y is 14
        self.hidingSpotList = list(self.hidingSpot)
        self.hidingSpotList[0] = 14
        self.hidingSpotList[1] = 14
        while gameState.hasWall(self.hidingSpotList[0], self.hidingSpotList[1]):
          self.hidingSpotList[0] = self.hidingSpotList - 1
        self.hidingSpot = tuple(self.hidingSpotList)
        return self.findPath(gameState, self.hidingSpot)[0]
      elif self.getColor(gameState) == "Blue": # Blue Team
        # X is 16 and Y is 14 or 13
        self.hidingSpotList = list(self.hidingSpot)
        self.hidingSpotList[0] = self.start[0]/2 + 1
        self.hidingSpotList[1] = self.start[1]
        while gameState.hasWall(self.hidingSpotList[0], self.hidingSpotList[1]):
          self.hidingSpotList[0] = self.hidingSpotList + 1
        self.hidingSpot = tuple(self.hidingSpotList)
        return self.findPath(gameState, self.hidingSpot)[0]
    return self.foodCollection(gameState)

class SouthAgent(DummyAgent):
  """
  This agent hides on the south side of the map.
  """
  def chooseAction(self, gameState):

    # Determine whether we're in hiding place
    if self.hidingSpot[0] == gameState.getAgentPosition(self.index)[0] and self.hidingSpot[1] == gameState.getAgentPosition(self.index)[1]:
      self.inHiding = True
      self.doneHiding = True
      self.attacking = True
    if self.inHiding == True:
      turnsToWait = 6
      # Leave hiding spot after number of turns
      if self.counter == turnsToWait:
        self.inHiding = False
      # increment counter and return stop action
      else:
        self.counter += 1
        return 'Stop'     

    #Get hiding location and go there
    if self.inHiding == False and self.doneHiding == False:
      if self.getColor(gameState) == "Red": # Red team
        # X is 14 and Y is 1 or 2
        self.hidingSpotList = list(self.hidingSpot)
        self.hidingSpotList[0] = 14
        self.hidingSpotList[1] = self.start[1]
        while gameState.hasWall(self.hidingSpotList[0], self.hidingSpotList[1]):
          self.hidingSpotList[0] = self.hidingSpotList - 1
        self.hidingSpot = tuple(self.hidingSpotList)
        return self.findPath(gameState, self.hidingSpot)[0]
      elif self.getColor(gameState) == "Blue": # Blue Team
        # X is 16 and Y is 1 or 2
        self.hidingSpotList = list(self.hidingSpot)
        self.hidingSpotList[0] = self.start[0]/2 + 1
        self.hidingSpotList[1] = 1
        while gameState.hasWall(self.hidingSpotList[0], self.hidingSpotList[1]):
          self.hidingSpotList[0] = self.hidingSpotList + 1
        self.hidingSpot = tuple(self.hidingSpotList)
        return self.findPath(gameState, self.hidingSpot)[0]
    return self.foodCollection(gameState)

