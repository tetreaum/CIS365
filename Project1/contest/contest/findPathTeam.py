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
    self.inHiding = False
    # Hold the coordinates for where we'll hide
    self.hidingSpot = [0, 0]
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    '''
    Your initialization code goes here, if you need any.
    '''

  # def chooseAction(self, gameState):
  #   """
  #   Picks among actions randomly.
  #   """
  #   if self.counter == 0:
  #     return self.findPath(gameState, ())

  #   return self.findPath(gameState, (10,11))

    # nearestFood = self.findNearestFood(gameState)
    # return self.findPath(gameState,nearestFood)

  def findNearestFood(self, gameState):
    nearestFoodDistance = 9999
    nearestFood = (1,1)
    for food in self.getFood(gameState).asList():
      dist = self.getMazeDistance(gameState.getAgentPosition(self.index),food)   
      if dist < nearestFoodDistance:
        nearestFoodDistance = dist
        nearestFood = food
    return nearestFood

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

  def getSuccessor(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  
  #Determine which color team is, this is used to determine hiding location
  def getColor(self, gameState):
    # self.start = gameState.getAgentPosition(self.index)
    # Red team starts at x = 1, blue is at x = 30 
    if self.start[0] < 2:
      return "Red"
    else:
      return "Blue"

class NorthAgent(DummyAgent):

  def chooseAction(self, gameState):

    team = self.getTeam(gameState)
    opp = self.getOpponents(gameState)
    
    if self.hidingSpot[0] == gameState.getAgentPosition(self.index)[0] and self.hidingSpot[1] == gameState.getAgentPosition(self.index)[1]:
      self.inHiding = True
    
    if self.inHiding == True:
      turnsToWait = 10
      # if self.counter == numturns to wait
        # hiding = false
        # return stop action
        # increment turn counter
      if self.counter == turnsToWait:
        self.inHiding = False
      # else
      #   find path to spot
      else:
        self.counter += 1
        return self.findPath(gameState, self.hidingSpot)

    #Get hiding location and go there
    else:
      if self.getColor == "Red": # Red team
        # Used to determine x coordinate of hiding location
        blueStart = gameState.getAgentPosition(opp[0])
        # X is 14 and Y is 14/13
        self.hidingSpot[0] = blueStart[0]/2 - 1
        self.hidingspot[1] = self.start[1]
        return self.findPath(gameState, self.hidingSpot)
      elif self.getColor == "Blue": # Blue Team
        # X is 16 and Y is 14 or 13
        self.hidingSpot[0] = self.start[0]/2 + 1
        self.hidingspot[1] = self.start[1]
        return self.findPath(gameState, self.hidingSpot)

class SouthAgent(DummyAgent):

  def chooseAction(self, gameState):

    team = self.getTeam(gameState)
    opp = self.getOpponents(gameState)
    
    if self.hidingSpot[0] == gameState.getAgentPosition(self.index)[0] and self.hidingSpot[1] == gameState.getAgentPosition(self.index)[1]:
      self.inHiding = True
    
    if self.inHiding == True:
      turnsToWait = 10
      # if self.counter == numturns to wait
        # hiding = false
        # return stop action
        # increment turn counter
      if self.counter == turnsToWait:
        self.inHiding = False
      # else
      #   find path to spot
      else:
        self.counter += 1
        return self.findPath(gameState, self.hidingSpot)

    #Get hiding location and go there
    else:
      if self.getColor == "Red": # Red team
        # Used to determine x coordinate of hiding location
        blueStart = gameState.getAgentPosition(opp[0])
        # X is 14 and Y is 1 or 2
        self.hidingSpot[0] = blueStart[0]/2 - 1
        self.hidingspot[1] = self.start[1]
        return self.findPath(gameState, self.hidingSpot)
      elif self.getColor == "Blue": # Blue Team
        # Used to determine y coordinate of hiding location
        redStart = gameState.getAgentPosition(opp[0])
        # X is 16 and Y is 1 or 2
        self.hidingSpot[0] = self.start[0]/2 + 1
        self.hidingspot[1] = redStart[1]
        return self.findPath(gameState, self.hidingSpot)