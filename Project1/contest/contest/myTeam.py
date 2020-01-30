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
    # This counter tells us when to hide/attack
    self.counter = 0
    # Determines what the agent is doing
    self.inHiding = False
    self.doneHiding = False
    self.attacking = False
    self.defending = False
    # Hold the coordinates for where we'll hide
    self.hidingSpot = (0, 0)
    self.hidingSpotList = [0, 0]
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    '''
    Your initialization code goes here, if you need any.
    '''

  # Find the nearest food from the agent
  def findNearestFood(self, gameState):
    nearestFoodDistance = 9999
    nearestFood = (1,1)
    for food in self.getFood(gameState).asList():
      dist = self.getMazeDistance(gameState.getAgentPosition(self.index),food)   
      if dist < nearestFoodDistance:
        nearestFoodDistance = dist
        nearestFood = food
    return nearestFood

  # Returns the action that gets us closer to the given position
  def findPath(self, gameState, position):
    bestDist = 9999
    actions = gameState.getLegalActions(self.index)
    for action in actions:
      successor = self.getSuccessor(gameState, action)
      pos2 = successor.getAgentPosition(self.index)
      dist = self.getMazeDistance(position,pos2)
      if dist < bestDist:
        bestAction = action
        bestDist = dist
    return bestAction

  # Get potential successors, used to help determine a move
  def getSuccessor(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  # Determine which color team is, this is used to determine hiding location
  def getColor(self, gameState):
    # Red team starts at x = 1, blue is at x = 30 
    if self.start[0] < 2:
      return "Red"
    else:
      return "Blue"

  # Evaluate actions
  def evaluate(self, gameState, action):

    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

class NorthAgent(DummyAgent):

  def chooseAction(self, gameState):

    # List of legal actions
    actions = gameState.getLegalActions(self.index)
    
    # Determine if we're hiding
    if self.hidingSpot[0] == gameState.getAgentPosition(self.index)[0] and self.hidingSpot[1] == gameState.getAgentPosition(self.index)[1]:
      self.inHiding = True
    
    if self.inHiding == True:
      turnsToWait = 10
      # Check if we're ready to move out of hiding
      if self.counter == turnsToWait:
        self.inHiding = False
        self.doneHiding = True
        self.attacking = True
        # FIXME return collect food
      # else return stop and increment counter
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
        return self.findPath(gameState, self.hidingSpot)
      elif self.getColor(gameState) == "Blue": # Blue Team
        # X is 16 and Y is 14 or 13
        self.hidingSpotList = list(self.hidingSpot)
        self.hidingSpotList[0] = self.start[0]/2 + 1
        self.hidingSpotList[1] = self.start[1]
        while gameState.hasWall(self.hidingSpotList[0], self.hidingSpotList[1]):
          self.hidingSpotList[0] = self.hidingSpotList + 1
        self.hidingSpot = tuple(self.hidingSpotList)
        return self.findPath(gameState, self.hidingSpot)

    features = [self.getFeatures(gameState, a) for a in actions]
    weights = [self.getWeights(gameState, a) for a in actions]

    # FIXME Generic Attacking/Defending
    if self.attacking == True and gameState.getAgentState(self.index).numCarrying < 10 and self.getScore(gameState) <= 0:
      # Collect Food
      # print(features)
      bestActions = []
      closeFoodPos = []
      tempPos = []
      a = 0
      for dct in features:
        for k, v in dct.items():
          if k == 'closeFood':
            tempPos.append(dct['closeFood'])
          if k == 'distanceToFood':
            bestActions.append(v)
            a = a + 1
      
      minVal = min(bestActions)
      i = bestActions.index(minVal)
      closeFoodPos = tuple(tempPos[i])

      print(bestActions)
      #bestActions = [a for a, v in zip(actions, values) if v == maxValue]
      return self.findPath(gameState, closeFoodPos)

      # if self.attacking == True and gameState.getAgentState(self.index).numCarrying > 10:
      #   homeBase = []
      #   if self.getColor(gameState) == "Red":
          
      #   elif self.getColor(gameState) == "Blue":  
    # if self.getScore() > 0:
    #   # Play Defense

    #DELETE LATER
    return random.choice(actions)

  # Get list of features
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
		
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
		
    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)
	
    # Compute distance to the nearest food
    if len(foodList) > 0: 
      myPos = successor.getAgentState(self.index).getPosition()
      # minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      # features['distanceToFood'] = minDistance
      minDistance = 9999
      closestFood = [0, 0]
      for food in foodList:
        if minDistance > self.getMazeDistance(myPos, food):
          minDistance = self.getMazeDistance(myPos, food)
          closestFood = food
      closeFood = tuple(closestFood)
      features['distanceToFood'] = minDistance
      features['closeFood'] = closeFood
      
      # features['closeEnemy'] = 0
      # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      # risk = [a for a in enemies if not a.isPacman and a.getPosition != None]
      # if len(risk) > 0:
      #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in risk]
      #   features['enemyDistance'] = min(dists)
      #   if (dist <= 4 for dist in dists):
      #     features['closeEnemy'] = 1
    return features

  # Get weights
  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'risk': -1, 'closeEnemy': -100}

class SouthAgent(DummyAgent):

  def chooseAction(self, gameState):

    #List of legal actions
    actions = gameState.getLegalActions(self.index)

    # Determine whether we're in hiding place
    if self.hidingSpot[0] == gameState.getAgentPosition(self.index)[0] and self.hidingSpot[1] == gameState.getAgentPosition(self.index)[1]:
      self.inHiding = True
      self.doneHiding = True
      self.attacking = True
    if self.inHiding == True:
      turnsToWait = 10
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
        return self.findPath(gameState, self.hidingSpot)
      elif self.getColor(gameState) == "Blue": # Blue Team
        # X is 16 and Y is 1 or 2
        self.hidingSpotList = list(self.hidingSpot)
        self.hidingSpotList[0] = self.start[0]/2 + 1
        self.hidingSpotList[1] = 1
        while gameState.hasWall(self.hidingSpotList[0], self.hidingSpotList[1]):
          self.hidingSpotList[0] = self.hidingSpotList + 1
        self.hidingSpot = tuple(self.hidingSpotList)
        return self.findPath(gameState, self.hidingSpot)
    
    # FIXME Generic Attacking/Defending
    if self.attacking == True and gameState.getAgentState(self.index).numCarrying < 10 and self.getScore(gameState) <= 0:
      # Collect Food
      features = [self.getFeatures(gameState, a) for a in actions]
      weights = [self.getWeights(gameState, a) for a in actions]
      print(features)
      bestActions = []
      closeFoodPos = []
      tempPos = []
      #a = 0
      for dct in features:
        for k, v in dct.items():
          if k == 'closeFood':
            tempPos.append(dct['closeFood'])
          if k == 'distanceToFood':
            bestActions.append(v)
            #a = a + 1
      
      minVal = min(bestActions)
      i = bestActions.index(minVal)
      closeFoodPos = tuple(tempPos[i])

      print(bestActions)
      #bestActions = [a for a, v in zip(actions, values) if v == maxValue]
      return self.findPath(gameState, closeFoodPos)
    
    # if gameState.getAgentState(self.index).numCarrying > 10:
    #   # Return to base

    # if self.getScore() > 0:
    #   # Play Defense
    
    #FIXME DELETE LATER 
    return random.choice(actions)

  # Get list of features 
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: 
      features['onDefense'] = 0

    # Computes closest food
    if len(foodList) > 0: 
      myPos = successor.getAgentState(self.index).getPosition()
      # minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      # features['distanceToFood'] = minDistance
      minDistance = 9999
      closestFood = [0, 0]
      for food in foodList:
        if minDistance > self.getMazeDistance(myPos, food):
          minDistance = self.getMazeDistance(myPos, food)
          closestFood = food
      closeFood = tuple(closestFood)
      features['distanceToFood'] = minDistance
      features['closeFood'] = closeFood

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)
      features['reverse'] = -1

    if action == Directions.STOP: 
      features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: 
      features['reverse'] = 1

    return features

  # Get weights
  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -20, 'stop': -100, 'reverse': -4}
