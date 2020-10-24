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
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    # draw layout with dead end routes and their exits
    self.debugDraw(list(getSpl(gameState, False)[2]), [0,1,0], clear=False)
    self.debugDraw(list(getSpl(gameState, False)[3]), [0,1,0], clear=False)
    self.debugDraw(list(getSpl(gameState, True)[2]), [0,1,0], clear=False)
    self.debugDraw(list(getSpl(gameState, True)[3]), [0,1,0], clear=False)
    self.debugDraw(list(getOut(gameState, True).keys()), [0,1,1], clear=False)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    #start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    #print(values)
    #print ("eval time for agent %d: %.4f" % (self.index, time.time() - start))

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights
    #返回他们的乘积一个number作为value

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    print(features)
    return features
    #返回一个counter，{'successorScore': 分数score}

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)
    score = self.getScore(gameState)
    foodInPac = 20 - (len(foodList) + score)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    initialPos = gameState.getInitialAgentPosition(self.index)
    goBack = False
    # Every time have 5 food in pac then go back 
    if (foodInPac >4):
      goBack = True
    else: goBack = False
  
    # Compute distance to the nearest food
    if goBack==False: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    else: features['distanceToFood'] = 0
    
    # Avoid the enemy
    if len(ghosts) >0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
      features['ghostDistance'] = min(dists)
    else: 
      features['ghostDistance'] = 0
    
    # Avoid stop
    if action == Directions.STOP: features['stop'] = 1
    else: features['stop'] = 0

    #go back to initial state
    if goBack == True:
      dist = self.getMazeDistance(myPos, initialPos)
      features['goBack'] = dist
      features['successorScore'] = 0
      features['distanceToFood'] = 0
    else:
      features['goBack'] = 0

    # Avoid reverse
    # rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    # if action == rev: features['reverse'] = 1

    if len(ghosts) >0:
        if myPos in getSpl(gameState, self.red):
            features['inDeadEnd'] = 1
        else: features['inDeadEnd'] = 0
    else: features['inDeadEnd'] = 0
    
    #print(len(foodList))
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 50, 'distanceToFood': -1, 'ghostDistance': 5, 'stop': -100, 'goBack': -1, 'inDeadEnd': -10}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    #print(gameState.getAgentState(self.index).scaredTimer)

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)
    #print(features['invaderDistance'])

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -500, 'stop': -100, 'reverse': -2}

######################################
# Helper functions of reading layout #
######################################

def getMyLine(gameState, red):
    '''
    Return a list of positions of my side bounary, excluding walls.
    我方半场的边界
    '''
    a = gameState.data.layout.width // 2
    if red:
        a= a - 1
    ls = []
    for y in range(1, gameState.data.layout.height):
        if not gameState.hasWall(a, y):
            ls.append((a, y))
    return ls

def getOppoLine(gameState, red):
    '''
    Return a list of positions of opponent bounary, excluding walls.
    对方半场的边界
    '''
    a = gameState.data.layout.width // 2
    if not red:
        a = a - 1
    ls = []
    for y in range(1, gameState.data.layout.height):
        if not gameState.hasWall(a, y):
            ls.append((a, y))
    return ls

def getAroundPositions(gameState, pos):
    '''
    Given a position, return set of adjacent positions up, down, left and right, excluding walls.
    周围不包括墙
    '''
    list1 = [(int(pos[0])-1,int(pos[1])), (int(pos[0])+1,int(pos[1])), (int(pos[0]),int(pos[1]+1)), (int(pos[0]),int(pos[1]-1))]
    set1 = set(list1)
    for i in range(len(list1)):
        a, b = list1[i]
        if gameState.hasWall(a,b):
            set1.remove((a,b))
    return set1

def getSpl(gameState, red):
    '''
    Return a list of all special positions, 
    including dead end and corrider leads to a dead end on the layout.
    Returned list[2] and [3] are special postions on opponents side of layout.
    Returned list[0] and [1] are special postions on opponents side of layout.
    特殊位置：死胡同
    '''
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

def getOut(gameState, isRed):
    '''
    Return a dictionary contains all exitPosition-deadEndorCorrider pairs
    返回出口-死胡同的dictionary
    '''
    dic = {}
    set1 = set()
    for x in range(1, gameState.data.layout.width):
        for y in range(1, gameState.data.layout.height):
            if not gameState.hasWall(x, y):
                tem_set = getAroundPositions(gameState, (x, y))
                dic[(x, y)] = tem_set
                if 1 == len(tem_set):
                    set1.add((x, y))
    dic2 = {}
    c_set = set1.copy()
    out = {}
    for i in set1:
        tem_set = dic[i]
        q = list(tem_set)
        dic2[i] = [i]
        while len(q) != 0:
            item = q.pop()
            if item not in dic.keys():
                dic[item] = getAroundPositions(gameState, item)
            tem_set2 = dic[item]
            if len(tem_set2) != 2:
                out[item]=dic2[i]
                continue
            else:
                c_set.add(item)
                dic2[i].append(item)
            for j in tem_set2:
                if j not in c_set:
                    q.append(j)
    return out

def doGetOut(out, p):
    '''
    Given an position p, return exit postion of that position.
    找位置对应的出口
    '''
    for i, j in out.items():
        if p in j:
            return i
    return None