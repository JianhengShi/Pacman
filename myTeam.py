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

import operator
import collections
import numpy as np
from game import Actions
from game import Directions
from util import Queue
from util import PriorityQueue
from captureAgents import CaptureAgent

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'Agent', second = 'Agent'):
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

class Agent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        self.state = gameState
        self.go_home = False
        self.my_dots = self.getMyDots(gameState)
        self.queue = Queue()
        self.spl = getSpl(gameState, self.red)
        self.out = getOut(gameState, self.red)
  
    def chooseAction(self, gameState):
        if self.ifCatch(gameState):
            output = self.catch(gameState)
        else:
            if not gameState.getAgentState(self.index).isPacman:
                output = self.eatFoodAction(gameState)
            else:
                if self.ifChase(gameState):
                    output = self.eatFoodAction(gameState)
                elif (len(self.getDots(gameState)) <= 2) or (gameState.data.timeleft < 30 and gameState.getAgentState(self.index).numCarrying > 0):
                    output = self.goHome(gameState)
                else:
                    output = self.eatFoodAction(gameState)
        self.state = gameState
        return output

    def ifCatch(self, gameState):
        if len(self.getDots(gameState)) <= 2 and gameState.getAgentState(self.index).numCarrying == 0:
            return True
        if gameState.getAgentState(self.index).scaredTimer > 0:
            return False
        a = 0
        b = 0
        for i in self.enemyPIndex(gameState):
            a += self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(i).getPosition())
            b += self.getMazeDistance(gameState.getAgentState(self.anotherIndex(gameState)).getPosition(), gameState.getAgentState(i).getPosition())
        if a < b <2:
            return True
        else:
            return False

    def catch(self, gameState):
        ls = []
        ls2 = []
        for i in self.getOpponents(gameState):
            if gameState.getAgentState(i).isPacman:
                ls.append(i)
                ls2.append(gameState.getAgentState(i).getPosition())
        a = None
        b = 99999999
        for j in ls2:
            if j is not None:
                path = self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [j], self.notGo(gameState))
                if path is None:
                    continue
                if len(path) < b:
                    b = len(path)
                    a = path
            
        if a is None or len(a) == 0:
            return Directions.STOP
        return a[0]

    def eatFoodAction(self, gameState):
        if self.go_home:
            return self.goHome(gameState)
        ls = []
        if len(self.getDots(gameState)) > 10:
            dic = dict()
            for i in self.getDots(gameState):
                dic.update({i: self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), i)})
            ls1 = []
            for i in sorted(dic.items(), key=operator.itemgetter(1)):
                ls1.append(i[0])
            ls = ls1[0: 10]
        else:
            ls = self.getDots(gameState)
        dic3 = dict()
        for i in ls:
            if self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [i], self.notGo(gameState)) is None:
                continue
            dic3.update({i: len(self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [i], self.notGo(gameState)))})
        if len(dic3) == 0:
            return self.goHome(gameState)
        out = sorted(dic3.items(), key=operator.itemgetter(1))[0][0]
        out_val = sorted(dic3.items(), key=operator.itemgetter(1))[0][1]
        dic4 = dict()
        ls2 = []
        if len(self.getDots(gameState)) > 10:
            dic = dict()
            for i in self.getDots(gameState):
                dic.update({i: self.getMazeDistance(gameState.getAgentState(self.anotherIndex(gameState)).getPosition(), i)})
            ls1 = []
            for i in sorted(dic.items(), key=operator.itemgetter(1)):
                ls1.append(i[0])
            ls2 = ls1[0: 10]
        else:
            ls2 = self.getDots(gameState)

        for eat in ls2:
            path = self.aStarSearch(gameState, gameState.getAgentState(self.anotherIndex(gameState)).getPosition(), [eat], self.notGo(gameState))
            if path is None:
                continue
            dic4.update({eat: len(path)})
        if len(dic4) != 0:
            out2 = sorted(dic4.items(), key=operator.itemgetter(1))[0][0]
            out2_val = sorted(dic4.items(), key=operator.itemgetter(1))[0][1]
            if out == out2 and out_val > out2_val and len(dic3) > int(len(self.my_dots)/3):
                out = sorted(dic3.items(), key=operator.itemgetter(1))[1][0]
            if out == out2 and out_val > out2_val and 3<=len(dic3) <= int(len(self.my_dots)/3): 
                out = sorted(dic3.items(), key=operator.itemgetter(1))[2][0]
            if len(self.getDots(gameState)) <= 4 and out_val > out2_val:
                if gameState.getAgentState(self.index).numCarrying > 0:
                    return self.goHome(gameState)
                else:
                    return self.catch(gameState)
        return self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [out], self.notGo(gameState))[0]

    def goHome(self, gameState):
        if len(self.homeWay(gameState)) == 0:
            return Directions.STOP
        return self.homeWay(gameState)[0]

    def ifChase(self, gameState):
        for i in self.enemyGIndex(self.state):
            for j in self.enemyGIndex(gameState):
                if i == j:
                    if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(j).getPosition()) <= self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(i).getPosition()) <= 3:
                        return True          
        return False

    def CapOrHome(self, gameState):
        way = self.homeWay(gameState)
        if len(way) > 0 and ((len(self.getDots(gameState)) <= 2) or(gameState.data.timeleft < 20 and gameState.getAgentState(self.index).numCarrying > 0) or (len(way) <= 5 and gameState.getAgentState(self.index).numCarrying >= 4 and not self.oppoPac(gameState))):
            return way[0]
        mostDangerous = self.notGo2(gameState)
        a = None
        b = 999999  
        for i in self.getCapsules(gameState):
            path = self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [i], mostDangerous)
            if path is None:
                continue
            if len(path) < b:
                b = len(path)
                a = i
        if a is not None:
            return self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [a], mostDangerous)[0]
        else:
            if len(way) == 0:
                return Directions.STOP
            else:
                return way[0]

    def ifGoHome(self, gameState):
        if not self.ifAtDeadRoute(gameState):
            return False
        if self.go_home is True:
            return True
        if self.ifAtDeadRoute(gameState):
            if doGetOut(self.out, gameState.getAgentState(self.index).getPosition()) is None:
                return False
            g = None
            a = 999999
            for ghost in self.enemyGIndex(gameState):
                if self.getMazeDistance(gameState.getAgentState(ghost).getPosition(), doGetOut(self.out, gameState.getAgentState(self.index).getPosition())) < a:
                    a = self.getMazeDistance(gameState.getAgentState(ghost).getPosition(), doGetOut(self.out, gameState.getAgentState(self.index).getPosition()))
                    g= ghost
            if a-self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), doGetOut(self.out, gameState.getAgentState(self.index).getPosition()))<1:
                return True
        return False

    def ifAtDeadRoute(self, gameState):
        ls = list(self.spl[2])+list(self.spl[2])
        if gameState.getAgentState(self.index).getPosition() in ls:
            return True
        else:
            return False

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

    def getMyDots(self, gameState):
        return self.getFoodYouAreDefending(gameState).asList() + self.getCapsulesYouAreDefending(gameState)

    def oppoPac(self, gameState):
        return gameState.getAgentState(self.getOpponents(gameState)[0]).isPacman and gameState.getAgentState(self.getOpponents(gameState)[1]).isPacman

    def enemyPosition(self, gameState):
        lis = []
        if gameState.getAgentPosition(self.getOpponents(gameState)[0]) is not None:
            lis.append(self.getOpponents(gameState)[0])
        if gameState.getAgentPosition(self.getOpponents(gameState)[1]) is not None:
            lis.append(self.getOpponents(gameState)[1])
        return lis

    def enemyGIndex(self, gameState):
        output = []
        for i in self.enemyPosition(gameState):
            if not gameState.getAgentState(i).isPacman and gameState.getAgentState(i).scaredTimer<=5:
                output.append(i)
        return output

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

    def enemyGPosition(self, gameState):
        out = []
        for ghost in self.enemyGIndex(gameState):
            out.append(gameState.getAgentState(ghost).getPosition())
        return out

    def notGo(self, gameState):
        output = []
        output=self.enemyGPosition(gameState)
        for i in self.enemyGPosition(gameState):
            output=output+list(getAroundPositions(gameState, i))
            if i in getOppoLine(gameState, self.red):  
                for j in getAroundPositions(gameState, i):
                    if j in getMyLine(gameState, self.red) and gameState.getAgentState(self.index).scaredTimer == 0:
                        output.remove(j)
            if self.getMazeDistance(i, gameState.getAgentState(self.index).getPosition())<=4:
                output=output+list(self.spl[2])
                output=output+list(self.spl[3])
        for j in self.enemyPPosition(gameState):
            if self.red and j in getMyLine(gameState, self.red):
                output.append((int(j[0] + 1), int(j[1])))
            if not self.red and j in getMyLine(gameState, self.red):
                output.append((int(j[0] - 1), int(j[1])))
            if self.getMazeDistance(j, gameState.getAgentState(self.index).getPosition())<=4:
                output=output+list(self.spl[2])
                output=output+list(self.spl[3])
        if gameState.getAgentState(self.index).scaredTimer > 0:
            output=output+self.enemyPPosition(gameState)
            for k in self.enemyPPosition(gameState):
                output=output+list(getAroundPositions(gameState, k))
        return output

    def notGo2(self, gameState):
        output = []
        output=self.enemyGPosition(gameState)
        for i in self.enemyGPosition(gameState):
            output=output+list(getAroundPositions(gameState, i))
            if i in getOppoLine(gameState, self.red):  
                for j in getAroundPositions(gameState, i):
                    if j in getMyLine(gameState, self.red) and gameState.getAgentState(self.index).scaredTimer == 0:
                        output.remove(j)       
        for j in self.enemyPPosition(gameState):
            if self.red and j in getMyLine(gameState, self.red):
                output.append((int(j[0] + 1), int(j[1])))
            if not self.red and j in getMyLine(gameState, self.red):
                output.append((int(j[0] - 1), int(j[1])))
        if gameState.getAgentState(self.index).scaredTimer > 0:
            output=output+self.enemyPPosition(gameState)
            for k in self.enemyPPosition(gameState):
                output=output+list(getAroundPositions(gameState, k))
        return output    

    def anotherIndex(self, gameState):
        if self.index == self.getTeam(gameState)[0]:
            index = self.getTeam(gameState)[1]
        else:
            index = self.getTeam(gameState)[0]
        return index

    def homeWay(self, gameState):
        dp = self.notGo(gameState)
        p = gameState.getAgentState(self.index).getPosition()
        line = getMyLine(gameState, self.red)
        way = None
        a = 9999999
        for border in line:
            path = self.aStarSearch(gameState, p, [border], dp)
            if path is not None and len(path) < a:
                a = len(path)
                way = path
        if way is None:
            return []
        return way

    def getDots(self, gameState):
        return self.getFood(gameState).asList()

def getMyLine(gameState, red):
    a = gameState.data.layout.width // 2
    if red:
        a= a - 1
    ls = []
    for y in range(1, gameState.data.layout.height):
        if not gameState.hasWall(a, y):
            ls.append((a, y))
    return ls

def getOppoLine(gameState, red):
    a = gameState.data.layout.width // 2
    if not red:
        a = a - 1
    ls = []
    for y in range(1, gameState.data.layout.height):
        if not gameState.hasWall(a, y):
            ls.append((a, y))
    return ls

def getAroundPositions(gameState, pos):
    list1 = [(int(pos[0])-1,int(pos[1])), (int(pos[0])+1,int(pos[1])), (int(pos[0]),int(pos[1]+1)), (int(pos[0]),int(pos[1]-1))]
    set1 = set(list1)
    for i in range(len(list1)):
        a, b = list1[i]
        if gameState.hasWall(a,b):
            set1.remove((a,b))
    return set1

def getSpl(gameState, red):
    list1 = []
    map1 = {}
    target1 = set()
    for x in range(1,gameState.data.layout.width // 2):
        for y in range(1,gameState.data.layout.height):
            if not gameState.hasWall(x, y):
                map1[(x, y)] = getAroundPositions(gameState, (x, y))
                if len(getAroundPositions(gameState, (x, y)))==1 :
                    target1.add((x, y))
                else:
                    list1.append((x, y))
    target2 = set()
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
    list2 = []
    map2 = {}
    target3 = set()
    for x in range(gameState.data.layout.width // 2,gameState.data.layout.width):
        for y in range(1,gameState.data.layout.height):
            if not gameState.hasWall(x, y):
                map2[(x, y)] = getAroundPositions(gameState, (x, y))
                if len(getAroundPositions(gameState, (x, y)))==1:
                    target3.add((x, y))
                else:
                    list2.append((x, y))
    target4 = set()
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
    for corner in set1:
        tem_set = dic[corner]
        q = list(tem_set)
        dic2[corner] = [corner]
        while len(q) != 0:
            item = q.pop()
            if item not in dic.keys():
                dic[item] = getAroundPositions(gameState, item)
            tem_set2 = dic[item]
            if len(tem_set2) != 2:
                out[item]=dic2[corner]
                continue
            else:
                c_set.add(item)
                dic2[corner].append(item)
            for i in tem_set2:
                if i not in c_set:
                    q.append(i)
    return out

def doGetOut(out, p):
    for i, j in out.items():
        if p in j:
            return i
    return None