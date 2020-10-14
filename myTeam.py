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
import json
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

    self.allActions = [Directions.WEST,Directions.NORTH,Directions.EAST,Directions.SOUTH,Directions.STOP]
    self.featureKeys = ['distanceToFood', 'foodToEat', 'disNotGo', "disPac"]
    # print(self.features)
    self.weights = self.initWeights(self.allActions, self.featureKeys)
    # self.weights ={'West': {'distanceToFood': 1.0448083829761436, 'foodToEat': 1.0, 'ghostInRange': -2.972108795643406}, 'North': {'distanceToFood': 1.048234867461356, 'foodToEat': 1.0, 'ghostInRange': -4.905922613102293}, 'East': {'distanceToFood': 0.9992496152265813, 'foodToEat': 1.0, 'ghostInRange': 0.8780595764113851}, 'South': {'distanceToFood': 1.0886294360444848, 'foodToEat': 1.501473430614396, 'ghostInRange': -8.783971438723631}, 'Stop': {'distanceToFood': 1.0044728576407824, 'foodToEat': 1.0, 'ghostInRange': 0.011546752765986346}}
    # self.reward = 0
    # self.actionTaken = None
    self.alfa = 0.5
    self.gamma = 0.9
    self.epsilon = 0.05
    self.Q = 0
    self.QsPrime = 0
    self.spl = getSpl(gameState, self.red)
    self.width, self.height = gameState.getWalls().width, gameState.getWalls().height    
    print(self.spl)

  def chooseAction(self, gameState):
    state = gameState    
    # if state.data.timeleft < 1000 :
    #   record = open("record.txt","a")
    #   record.write(json.dumps(self.weights))
    #   record.close() 
    legalActions = state.getLegalActions(self.index)  
    if util.flipCoin(self.epsilon):
      print("exploring")
      optiAct = random.choice(legalActions)
    else:
      successors = []
      for legalAction in legalActions:
        successors.append((legalAction, self.getSuccessor(state, legalAction)))   
    
      # print("\ncurrent pos", state.getAgentState(self.index).getPosition())
      features = self.getFeatureValues(state, successors)
      # print("current state features", features)
      optiAct, self.Q = self.computeQ(features, legalActions)
      # print("action to take", optiAct)

      successor = self.getSuccessor(state, optiAct)
      # print("successor of optimal action", optiAct)
      reward = self.calReward(state, optiAct)
      # print("reward", reward)
      self.updateWeight(state, optiAct, successor, reward, features) 
    return optiAct

  def updateWeight(self, state, action, successor, reward, features):
    print("weights before update", self.weights)
    legalActions = successor.getLegalActions(self.index)   
    successors = []
    for legalAction in legalActions:
      successors.append((legalAction, self.getSuccessor(successor, legalAction))) 
    successorFeature = self.getFeatureValues(successor, successors)
    _ , Qsuccessor = self.computeQ(successorFeature, legalActions)

    for feature in self.weights[action]:
      oldW = self.weights[action][feature]
      # if feature == 'ghostInRange':
        # print(feature, features[action][feature])
      self.weights[action][feature] = oldW + self.alfa * (reward + self.gamma * Qsuccessor - self.Q) * features[action][feature]
    print("weights after update", self.weights)

  def calReward(self,state,action):
    reward = 0
    successor = self.getSuccessor(state, action)
    if successor.getAgentState(self.index).getPosition() in self.getFood(state).asList():
      reward += 4
      # print("eat bean reward")
    if successor.getAgentState(self.index).getPosition() in self.getGPosition(successor):
      reward -= 3
    if successor.getAgentState(self.index).getPosition() in self.notGo(state):
      reward -= 1
      # print("ghost reward")
    return reward

  def getFeatureValues(self, state, successors):
    features = self.initFeatures(self.allActions, self.featureKeys)
    for action, successor in successors:
      features[action]['distanceToFood'] = -self.getMinDisToFood(successor)
      # print(self.enemyGPosition(state))
      if state.getAgentState(self.index).isPacman and not self.enemyGPosition(state):
        # print("next pos", successor.getAgentState(self.index).getPosition() )
        # print("safe")
        # features[action]['ghostInRange'] = 0
        features[action]['foodToEat'] = self.getFoodNotEaten(state, successor)
      else:
        # print("next pos", successor.getAgentState(self.index).getPosition() )
        # print("Ghost is here!")
        # features[action]['ghostInRange'] = min([self.getMazeDistance(successor.getAgentState(self.index).getPosition(), ghost) for ghost in self.enemyGPosition(state)])/5
        features[action]['foodToEat'] = 0
      if state.getAgentState(self.index).isPacman and len(self.notGo(state)) != 0:
        features[action]['disNotGo'] = min([self.getMazeDistance(successor.getAgentState(self.index).getPosition(),loc) for loc in self.notGo(state)])/(self.height * self.width)
      else:
        features[action]['disNotGo'] = 0
      # print(min([self.getMazeDistance(successor.getAgentState(self.index).getPosition(),loc) for loc in self.spl]))
      print( self.notGo(state))
    # print("features", features)
    return features

  def getMinDisToFood(self,state):
    foodList = self.getFood(state).asList() 
    if len(foodList) > 0: 
      pos = state.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(pos, food) for food in foodList])
    return minDistance/(self.height * self.width)
  
  def getFoodNotEaten(self,state,successor):
    isFood = 0
    if successor.getAgentState(self.index).getPosition() in self.getFood(state).asList():
      isFood = 1
    return isFood
 
  def computeQ(self,features, legalActions):
    Qs = util.Counter()
    for action in legalActions:
      value = 0
      for feature in features[action].keys():
        value += features[action][feature] * self.weights[action][feature]
      Qs[action] = value
      # print(action, value)
    return (Qs.argMax(),Qs[Qs.argMax()])

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

  def initFeatures(self, allActions, featureKeys):
    features = util.Counter()
    for action in allActions:
      features[action] = {}
      for key in featureKeys:
        features[action][key] = 0
    return features

  def initWeights(self, allActions,featureKeys):
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

  def enemyPIndex(self, gameState):
    output = []
    for i in self.enemyPosition(gameState):
        if gameState.getAgentState(i).isPacman:
            output.append(i)
    return output

  def enemyGIndex(self, gameState):
    output = []
    for i in self.enemyPosition(gameState):
        if not gameState.getAgentState(i).isPacman and gameState.getAgentState(i).scaredTimer<=5:
            output.append(i)
    return output

  def enemyPosition(self, gameState):
    lis = []
    if gameState.getAgentPosition(self.getOpponents(gameState)[0]) is not None:
        lis.append(self.getOpponents(gameState)[0])
    if gameState.getAgentPosition(self.getOpponents(gameState)[1]) is not None:
        lis.append(self.getOpponents(gameState)[1])
    return lis

  def enemyGPosition(self, gameState):
    out = []
    for i in self.enemyGIndex(gameState):
        out.append(gameState.getAgentState(i).getPosition())
    return out

  def enemyPPosition(self, gameState):
    out = []
    for i in self.enemyPIndex(gameState):
        out.append(gameState.getAgentState(i).getPosition())
    return out

  def enemyPIndex(self, gameState):
    output = []
    for i in self.enemyPosition(gameState):
        if gameState.getAgentState(i).isPacman:
            output.append(i)
    return output

  def notGo(self, gameState):
    output = []
    output=self.enemyGPosition(gameState)
    for i in self.enemyGPosition(gameState):
        output=output+list(getAroundPositions(gameState, i))
        if i in getOppoLine(gameState, self.red):  
            for j in getAroundPositions(gameState, i):
                if j in getMyLine(gameState, self.red) and gameState.getAgentState(self.index).scaredTimer == 0:
                    output.remove(j)
        if self.getMazeDistance(i, gameState.getAgentState(self.index).getPosition())<=5:
            output=output+list(self.spl[2])
            output=output+list(self.spl[3])

    if gameState.getAgentState(self.index).scaredTimer > 0:
        output=output+self.enemyPPosition(gameState)
        for k in self.enemyPPosition(gameState):
            output=output+list(getAroundPositions(gameState, k))
    return output

def getAroundPositions(gameState, pos):
  list1 = [(int(pos[0])-1,int(pos[1])), (int(pos[0])+1,int(pos[1])), (int(pos[0]),int(pos[1]+1)), (int(pos[0]),int(pos[1]-1))]
  set1 = set(list1)
  for i in range(len(list1)):
      a, b = list1[i]
      if gameState.hasWall(a,b):
          set1.remove((a,b))
  return set1

def getOppoLine(gameState, red):
  a = gameState.data.layout.width // 2
  if not red:
      a = a - 1
  ls = []
  for y in range(1, gameState.data.layout.height):
      if not gameState.hasWall(a, y):
          ls.append((a, y))
  return ls

def getMyLine(gameState, red):
  a = gameState.data.layout.width // 2
  if red:
      a= a - 1
  ls = []
  for y in range(1, gameState.data.layout.height):
      if not gameState.hasWall(a, y):
          ls.append((a, y))
  return ls

def getSpl(gameState, red):
  # one half of layout
  list1 = []
  map1 = {}
  target1 = set() # dead ends which only have one legal adjacent position but walls
  for x in range(1,gameState.data.layout.width // 2):
      for y in range(1,gameState.data.layout.height):
          if not gameState.hasWall(x, y):
              map1[(x, y)] = getAroundPositions(gameState, (x, y))
              if len(getAroundPositions(gameState, (x, y)))==1 :
                  target1.add((x, y))
              else:
                  list1.append((x, y))
  target2 = set() # positions whose all adjacent positions are dead ends
  a = len(list1)
  b = 0
  while a != b:
      a = len(list1)
      lis1 = list1.copy()
      for i in lis1:
          if len(map1[i]) >= 2:
              c = 0
              for j in map1[i]:
                  if (j in target1) or (j in target2):
                      c += 1
              if c >= (len(map1[i]) - 1):
                  list1.remove(i)
                  target2.add(i)
      b= len(list1)
  # another half of layout
  list2 = []
  map2 = {}
  target3 = set() # dead ends which only have one legal adjacent position but walls
  for x in range(gameState.data.layout.width // 2,gameState.data.layout.width):
      for y in range(1,gameState.data.layout.height):
          if not gameState.hasWall(x, y):
              map2[(x, y)] = getAroundPositions(gameState, (x, y))
              if len(getAroundPositions(gameState, (x, y)))==1:
                  target3.add((x, y))
              else:
                  list2.append((x, y))
  target4 = set() # positions whose all adjacent positions are dead ends
  d = len(list2)
  e = 0
  while d != e:
      d = len(list2)
      lis2 = list2.copy()
      for i in lis2:
          if len(map2[i]) >= 2:
              f = 0
              for j in map2[i]:
                  if (j in target3) or (j in target4):
                      f += 1
              if f >= (len(map2[i]) - 1):
                  list2.remove(i)
                  target4.add(i)
      e = len(list2)
  return_list = []
  if red:
      return_list.append(target1)
      return_list.append(target2)
      return_list.append(target3)
      return_list.append(target4)
  else:
      return_list.append(target3)
      return_list.append(target4)
      return_list.append(target1)
      return_list.append(target2)
  return return_list

    