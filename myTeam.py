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
from util import PriorityQueue
from game import Actions
import collections
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAgent', second = 'DefensiveAgent'):
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

class QLearningCaptureAgent(CaptureAgent):
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
    self.offensiveFeatureKeys = ['distanceToFood', 'foodToEat', 'disNotGo', 'ghostInRange']
    self.defensiveFeatureKeys = ["disPac", "onDefend", "disFoodToDefend","disPac_scared","disFoodToDefend_scared" ]
    # print(self.features)
    self.offensiveWeights = self.initWeights(self.allActions, self.offensiveFeatureKeys)
    self.defensiveWeights = self.initWeights(self.allActions, self.defensiveFeatureKeys)
    # if self.red:
    #   self.offensiveWeights = {'West': {'distanceToFood': 1.0190724247435337, 'foodToEat': 4.1958225635787905, 'disNotGo': 1.0156377321178731, 'ghostInRange': -0.016819800863038022}, 'North': {'distanceToFood': 0.920298113532667, 'foodToEat': 6.365757489774838, 'disNotGo': 1.6056778519918165, 'ghostInRange': -1.5495175318982441}, 'East': {'distanceToFood': 0.730999669772557, 'foodToEat': 4.09100390585325, 'disNotGo': 1.3550785176713904, 'ghostInRange': -1.699888001511586}, 'South': {'distanceToFood': 0.9632151655333985, 'foodToEat': 4.5643647156843095, 'disNotGo': 0.947592074670046, 'ghostInRange': -2.3396233409009057}, 'Stop': {'distanceToFood': 1.000022802983676, 'foodToEat': 1.0, 'disNotGo': 0.990822950670677, 'ghostInRange': -2.4090518892924004}}
    #   self.defensiveWeights = {'West': {'disPac': 0.9995891249694154, 'onDefend': 0.7286760134763696, 'disFoodToDefend': 1.000027817737563, 'distanceToFood': 1.0}, 'North': {'disPac': 0.9928425371641709, 'onDefend': 0.736070835410189, 'disFoodToDefend': 0.999787151985802, 'distanceToFood': 1.0}, 'East': {'disPac': 1.0006256686266357, 'onDefend': 0.7461377230837017, 'disFoodToDefend': 0.9998531720543097, 'distanceToFood': 1.0}, 'South': {'disPac': 0.9984402553814196, 'onDefend': 0.7187924367900846, 'disFoodToDefend': 0.9989345116712985, 'distanceToFood': 1.0}, 'Stop': {'disPac': 1.0018871553938655, 'onDefend': 0.7374011659424449, 'disFoodToDefend': 1.0000268404223416, 'distanceToFood': 1.0}}
    # else:
    #   self.offensiveWeights = {'West': {'distanceToFood': 0.8829870551965651, 'foodToEat': 4.223295293681011, 'disNotGo': 0.9799905995707912, 'ghostInRange': -2.0244860324419065}, 'North': {'distanceToFood': 0.9642070881561703, 'foodToEat': 4.035570890011501, 'disNotGo': 0.9105651326891779, 'ghostInRange': -7.03471892522429}, 'East': {'distanceToFood': 1.0161174407483016, 'foodToEat': 5.349758748151534, 'disNotGo': 0.9442628077382, 'ghostInRange': -4.837427444510008}, 'South': {'distanceToFood': 0.9084840999974431, 'foodToEat': 4.07015200765776, 'disNotGo': 0.9850700026348445, 'ghostInRange': -2.209448882896262}, 'Stop': {'distanceToFood': 1.0, 'foodToEat': 1.0, 'disNotGo': 0.9949068629413839, 'ghostInRange': -5.670802336990366}}
    #   self.defensiveWeights = {'West': {'disPac': 0.9991711436044567, 'onDefend': 1.0, 'disFoodToDefend': 0.9994280701913769, 'distanceToFood': 1.0}, 'North': {'disPac': 0.9996645554630801, 'onDefend': 1.0, 'disFoodToDefend': 0.9992189000082605, 'distanceToFood': 1.0}, 'East': {'disPac': 0.9997476256306012, 'onDefend': 1.0, 'disFoodToDefend': 0.9999983552868402, 'distanceToFood': 1.0}, 'South': {'disPac': 0.996045561608993, 'onDefend': 1.0, 'disFoodToDefend': 0.9999895840006816, 'distanceToFood': 1.0}, 'Stop': {'disPac': 0.9996967639507508, 'onDefend': 1.0, 'disFoodToDefend': 0.999998057698827, 'distanceToFood': 1.0}}
    # self.reward = 0
    # self.actionTaken = None
    self.alfa = 0.5
    self.gamma = 0.9
    self.epsilon = 0.00
    self.Q = 0
    self.QsPrime = 0
    self.spl = getSpl(gameState, self.red)
    self.width, self.height = gameState.getWalls().width, gameState.getWalls().height   
    self.mySide = getMyLine(gameState, self.red) 
    self.totalFood = len(self.getDots(gameState))
    self.eachRunFood = len(self.getDots(gameState))//3
    self.my_dots = self.getFoodYouAreDefending(gameState).asList()
    self.preScore = 0

  def chooseAction(self, gameState):
    state = gameState    
    if self.isOffensive():
      if (len(self.getDots(state)) <= 2) or (state.data.timeleft < 70 and state.getAgentState(self.index).numCarrying > 0) or (state.getAgentState(self.index).numCarrying > self.eachRunFood):
        optiAct = self.goHome(state)
      else:
        legalActions = state.getLegalActions(self.index)  
        if util.flipCoin(self.epsilon):
          optiAct = random.choice(legalActions)
        else:
          successors = []
          for legalAction in legalActions:
            successors.append((legalAction, self.getSuccessor(state, legalAction)))       
          # print("\ncurrent pos", state.getAgentState(self.index).getPosition())
          features = self.getFeatureValues(state, successors)
          # print("current state features", features)
          
          optiAct, self.Q = self.computeQ(features, legalActions, self.offensiveWeights)
          # print("action to take", optiAct)

          successor = self.getSuccessor(state, optiAct)
          # print("successor of optimal action", optiAct)
          reward = self.calReward(state, optiAct)
          # print("reward", reward)
          self.offensiveWeights = self.updateWeight(state, optiAct, successor, reward, features, self.offensiveWeights) 
      return optiAct
    else: 
      if len(self.eatenFoodPos(state)) != 0 and self.getMinDisToPac(state) == 0:
        optiAct = self.goEatenFoodWay(gameState)
      else:
        # print("\n", self.index, state.getAgentState(self.index).getPosition())
        legalActions = state.getLegalActions(self.index)  
        if util.flipCoin(self.epsilon):
          optiAct = random.choice(legalActions)
        else:
          successors = []
          for legalAction in legalActions:
            successors.append((legalAction, self.getSuccessor(state, legalAction)))    
          features = self.getFeatureValues(state, successors)
          # print("current state features", features)
          optiAct, self.Q = self.computeQ(features, legalActions, self.defensiveWeights)
          # print("action to take", optiAct)

          successor = self.getSuccessor(state, optiAct)
          reward = self.calReward(state, optiAct)
          self.defensiveWeights = self.updateWeight(state, optiAct, successor, reward, features, self.defensiveWeights) 
          # print(optiAct)
          self.my_dots = self.getFoodYouAreDefending(state).asList()
      return optiAct

  def computeQ(self,features, legalActions, weights):
    Qs = util.Counter()
    for action in legalActions:
      value = 0
      for feature in features[action].keys():
        value += features[action][feature] * weights[action][feature]
      # if not self.isOffensive():
      #   print("index, action, qvalue", self.index, action, value)
        
      Qs[action] = value
    # if not self.isOffensive():
    #   print(self.index, Qs.argMax(),Qs[Qs.argMax()])
    return (Qs.argMax(),Qs[Qs.argMax()])

  def updateWeight(self, state, action, successor, reward, features, weights):
    # print("weights before update", weights)
    legalActions = successor.getLegalActions(self.index)   
    successors = []
    for legalAction in legalActions:
      successors.append((legalAction, self.getSuccessor(successor, legalAction))) 
    successorFeature = self.getFeatureValues(successor, successors)
    _ , Qsuccessor = self.computeQ(successorFeature, legalActions, weights)

    for feature in weights[action]:
      oldW = weights[action][feature]
      weights[action][feature] = oldW + self.alfa * (reward + self.gamma * Qsuccessor - self.Q) * features[action][feature]
    # print("\nweights after update", weights)
    return weights

  def calReward(self,state,action):
    reward = 0
    successor = self.getSuccessor(state, action)
    if successor.getAgentState(self.index).getPosition() in self.getFood(state).asList():
      reward += 4
    if successor.getAgentState(self.index).getPosition() in self.notGo(state):
      reward -= 3
    if not successor.getAgentState(self.index).isPacman and successor.getAgentState(self.index).getPosition() in self.getPacPos(state):
      reward += 4
    return reward

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

  def getDots(self, gameState):
    return self.getFood(gameState).asList()

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

  def aStarSearch(self, gameState, start, goal, lis):
    pq = PriorityQueue()
    c_set = set()
    pq.push((start, [], float('inf')), 0)
    dic = collections.defaultdict(lambda: float('inf'))
    if goal[0] in lis:
        
        return None
    while not pq.isEmpty():
        node = pq.pop()
        if node[0] not in c_set or node[2] < dic[node[0]]:
            c_set.add(node[0])
            dic[node[0]] = node[2]
            if node[0] in goal:
                return node[1]
            actions = [Directions.WEST,Directions.NORTH,Directions.EAST,Directions.SOUTH,]
            successors = []
            for i in actions:
                x, y = node[0]
                dx, dy = Actions.directionToVector(i)
                if not gameState.getWalls()[int(x + dx)][int(y + dy)] and (int(x + dx), int(y + dy)) not in lis:
                    successors.append(((int(x + dx), int(y + dy)), i))
            for i, j in successors:
                pq.update((i, node[1] +[j],len(node[1]) + 1), len(node[1]) + 1 + max(self.getMazeDistance(i, goal)for goal in goal))

  def goHome(self, gameState):
    if len(self.homeWay(gameState)) == 0:
        return Directions.STOP
    return self.homeWay(gameState)[0]

  def homeWay(self, gameState):
    dp = self.notGo(gameState)
    p = gameState.getAgentState(self.index).getPosition()
    line = getMyLine(gameState, self.red)
    way = None
    a = 9999999
    for i in line:
        path = self.aStarSearch(gameState, p, [i], dp)
        if path is not None and len(path) < a:
            a = len(path)
            way = path
    if way is None:
        return []
    return way

  def eatenFoodPos(self, gameState):
    eatenFood = list(set(self.my_dots)-set(self.getFoodYouAreDefending(gameState).asList()))
    return eatenFood
  
  def eatenFoodWay(self, gameState, eatenFoodPos):
    dp = self.notGo(gameState)
    p = gameState.getAgentState(self.index).getPosition()
    way = None
    a = 9999999
    for pos in eatenFoodPos:
        path = self.aStarSearch(gameState, p, [pos], dp)
        if path is not None and len(path) < a:
            a = len(path)
            way = path
    if way is None:
        return []
    return way
  
  def goEatenFoodWay(self, gameState):
    if len(self.eatenFoodWay(gameState, self.eatenFoodPos(gameState))) == 0:
        return Directions.STOP
    return self.eatenFoodWay(gameState, self.eatenFoodPos(gameState))[0]

  def getFoodNotEaten(self,state,successor):
    isFood = 0
    if successor.getAgentState(self.index).getPosition() in self.getFood(state).asList():
      isFood = 1
    return isFood

  def getMinDisToGhost(self, state):
      gDis = [self.getMazeDistance(state.getAgentState(self.index).getPosition(), ghost) for ghost in self.enemyGPosition(state)]
      if len(gDis) == 0:
        return 0
      else:
        return min(gDis)/5
  
  def getPacPos(self, state):
    oppoPos = []
    for oppo in self.getOpponents(state):
      if state.getAgentState(oppo).isPacman and state.getAgentState(oppo).getPosition() is not None:
        oppoPos.append(state.getAgentState(oppo).getPosition())
    return oppoPos

  def getMinDisToPac(self, state):
    oppoPos = self.getPacPos(state)
    if len(oppoPos) == 0:
      return 0
    else:
      return min([self.getMazeDistance(state.getAgentState(self.index).getPosition(), pos) for pos in oppoPos])/(self.height * self.width)

  def getMinDisToNotGo(self, state):
    if len(self.notGo(state)) == 0:
      return 0
    else:
      return min([self.getMazeDistance(state.getAgentState(self.index).getPosition(), loc) for loc in self.notGo(state)])/(self.height * self.width)

  def getMinDisToFood(self,state):
    foodList = self.getFood(state).asList() 
    if len(foodList) > 0: 
      pos = state.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(pos, food) for food in foodList])
    return minDistance/(self.height * self.width)

class OffensiveAgent(QLearningCaptureAgent):
  def isOffensive(self):
    return True

  def initFeatures(self, allActions, featureKeys):
    features = util.Counter()
    for action in allActions:
      features[action] = {}
      for key in featureKeys:
        features[action][key] = 0
    return features

  def getFeatureValues(self, state, successors):
    features = self.initFeatures(self.allActions, self.offensiveFeatureKeys)
    for action, successor in successors:
      if state.getAgentState(self.index).isPacman or state.getAgentState(self.index).getPosition() in self.mySide:
        features[action]['disNotGo'] = self.getMinDisToNotGo(successor)
        features[action]['ghostInRange'] = self.getMinDisToGhost(successor)
        if not self.enemyGPosition(state):
          features[action]['foodToEat'] = self.getFoodNotEaten(state, successor)
          features[action]['distanceToFood'] = -self.getMinDisToFood(successor)
        else:
          features[action]['foodToEat'] = 0
          features[action]['distanceToFood'] = 0
      else:
        features[action]['foodToEat'] = self.getFoodNotEaten(state, successor)
        features[action]['distanceToFood'] = -self.getMinDisToFood(successor)
        features[action]['disNotGo'] = 0
        features[action]['ghostInRange'] = 0
    return features

class DefensiveAgent(QLearningCaptureAgent):  
  def isOffensive(self):
    return False

  def initFeatures(self, allActions, featureKeys):
    features = util.Counter()
    for action in allActions:
      features[action] = {}
      for key in featureKeys:
        features[action][key] = 0
    return features
    
  def getFeatureValues(self, state, successors):
    features = self.initFeatures(self.allActions, self.defensiveFeatureKeys)
    # print(self.isOnMySide(state))
    for action, successor in successors:
      features[action]["disPac_scared"] = 0
      features[action]["disFoodToDefend_scared"] = 0

      if self.isOnMySide(successor):
        features[action]["onDefend"] = 0
      else:
        features[action]["onDefend"] = -1
      
      if self.getMinDisToPac(state) == 0:
        features[action]["disPac"] = 0
        features[action]["disFoodToDefend"] = -self.getMaxDisToMyFood(successor)
      else:       
        if state.getAgentState(self.index).scaredTimer > 0:
          features[action]["disFoodToDefend"] = 0
          features[action]["disPac"] = 0
          features[action]["disPac_scared"] = self.getMinDisToPac(successor)
          features[action]["disFoodToDefend_scared"] = self.getMaxDisToMyFood(successor)
        else:
          features[action]["disPac"] = -self.getMinDisToPac(successor)   
          features[action]["disFoodToDefend"] = -self.getMaxDisToMyFood(successor)*0.5
    return features

  def isOnMySide(self, state):
    if self.red:
      if state.getAgentState(self.index).getPosition()[0] < self.mySide[0][0]:
        return True
      else:
        return False
    else:
      if state.getAgentState(self.index).getPosition()[0] > self.mySide[0][0]:
        return True
      else:
        return False

  def getMaxDisToMyFood(self, state):
    myFoodDis = [self.getMazeDistance(state.getAgentState(self.index).getPosition(), food) for food in self.getFoodYouAreDefending(state).asList()]
    if len(myFoodDis) == 0:
      return 0
    else:
      return max(myFoodDis)/(self.height * self.width)**2  

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



    