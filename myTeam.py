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
import random, time, util
from game import Directions
import game
import numpy as np
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAgent', second = 'OffensiveAgent'):
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
class OffensiveAgent(CaptureAgent):
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
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    allActions = [Directions.WEST,Directions.NORTH,Directions.EAST,Directions.SOUTH,Directions.STOP]
    featureKeys = ['score', 'distanceToFood', 'foodNotEaten', 'ghostInRange']
    self.features = self.initFeatures(allActions, featureKeys)
    # print(self.features)
    self.weights = self.initWeights(allActions, featureKeys)
    self.reward = None
    # print(self.weights)  

  def chooseAction(self, gameState):
    state = gameState
    legalActions = state.getLegalActions(self.index)
    successors = []
    for legalAction in legalActions:
      successors.append((legalAction, self.getSuccessor(state, legalAction))) 
    self.updateFeatureValues(successors)
    OptiAct = self.computeQ(legalActions)
    print("choose action")
    self.reward = self.calReward(state, successors)
    print(self.reward)
    return OptiAct

  def calReward(self,state,successors):
    reward = util.Counter()
    for action, successor in successors:
      print(action)
      reward[action] = -1
      rewardForScore = (successor.getScore() - state.getScore()) * 10 
      # print("rewardForScore:", rewardForScore)
      rewardForDisToFood = (self.getMinDisToFood(successor) - self.getMinDisToFood(state)) * (-1)
      # print("rewardForDisToFood:", rewardForDisToFood)
      rewardForFoodNotEaten = (self.getFoodNotEaten(successor) - self.getFoodNotEaten(state)) * (-2)
      # print("rewardForFoodNotEaten:", rewardForFoodNotEaten)
      print( )
      rewardForGhostInRange = (len(self.getGPosition(successor)) - len(self.getGPosition(state))) * (-10)
      # print("rewardForGhostInRange:", rewardForGhostInRange)
      # print(self.getGPosition(state))
      # print(self.getGPosition(successor))
      print("rewardForGhostInRange:", rewardForGhostInRange)
      total = rewardForScore + rewardForDisToFood + rewardForFoodNotEaten + rewardForGhostInRange
      reward[action] += total
    return reward

  def updateFeatureValues(self, successors):
    for action, successor in successors:
      if successor.isOnRedTeam(self.index):
        self.features[action]['score'] = self.getScore(successor)
      else:
        self.features[action]['score'] = -self.getScore(successor)
      self.features[action]['distanceToFood'] = -self.getMinDisToFood(successor)
      self.features[action]['foodNotEaten'] = -self.getFoodNotEaten(successor)
      self.features[action]['ghostInRange'] = -len(self.getGPosition(successor))

  def getMinDisToFood(self,state):
    foodList = self.getFood(state).asList() 
    if len(foodList) > 0: 
      pos = state.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(pos, food) for food in foodList])
    return minDistance    
  
  def getFoodNotEaten(self,state):
    foodNum = len(self.getFood(state).asList())
    return foodNum
 
  def computeQ(self,legalActions):
    Qs = util.Counter()
    for action in legalActions:
      value = 0
      for feature in self.features[action].keys():
        value += self.features[action][feature] * self.weights[action][feature]
      Qs[action] = value
    return Qs.argMax()

  def getSuccessor(self, state, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = state.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def initFeatures(self,allActions, featureKeys):
    features = util.Counter()
    for action in allActions:
      features[action] = {}
      for key in featureKeys:
        features[action][key] = 0
    return features

  def initWeights(self,allActions,featureKeys):
    weights = util.Counter()
    for action in allActions:
      weights[action] = {}
      for key in featureKeys:
        weights[action][key] = 1
    return weights

  def getGPosition(self, state):
    ghostsPos = []
    for i in self.getOpponents(state):
      if state.getAgentPosition(i) is not None:
        ghostsPos.append(state.getAgentPosition(i))
    return ghostsPos