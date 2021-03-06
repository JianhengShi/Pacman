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
import collections, time, random, util
#import numpy as np
from game import Actions
from game import Directions
from util import Queue
from util import PriorityQueue
from captureAgents import CaptureAgent
import random

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
        '''
        Initialize state.
        '''
        CaptureAgent.registerInitialState(self, gameState)
        self.state = gameState
        self.go_home = False
        self.my_dots = self.getMyDots(gameState)
        self.queue = Queue()
        self.spl = getSpl(gameState, self.red)
        self.out = getOut(gameState, self.red)
        self.pos = [] #List of position history
        self.underchasing = [] #List of uder chasing history
        self.stuckThreshold = 15
        self.safeBreakTie = 2
        self.seduction=False
  
    def chooseAction(self, gameState):  
        '''
        Logic of choosing action.
        Strategy that emphasizes offense.
        '''
        # If teh agent is stuck
        if len(self.pos) == self.stuckThreshold and self.ifStuck():
            output = self.breaktie(gameState)
        elif self.ifCatch(gameState):
            output = self.catch(gameState)
        else:
            # If the agent is ghost, go back to offense
            if not gameState.getAgentState(self.index).isPacman:
                output = self.eatDots(gameState)
            # If the agent is Pacman
            else:               
                # If eats 18 dots or time is up
                if (len(self.getDots(gameState)) <= 2) or (gameState.data.timeleft < 80 and gameState.getAgentState(self.index).numCarrying > 0) or self.ifLongChasing():
                    if not gameState.getAgentState(self.index).isPacman:
                        return catch(gameState)
                    else:
                        output = self.goHome(gameState)
                # If under chasing, run away with MCTS
                elif self.ifChase(gameState):
                    if len(self.getDots(gameState)) > 0:
                        rootNode = Node(gameState,self,None,None, self.enemyGPosition(gameState), getMyLine(gameState, gameState.isOnRedTeam(self.index)))
                        print ('run away with MCTS')
                        output = MCTS(rootNode)
                    else:
                        output = self.goHome(gameState)
                # Otherwise, eat dots
                else:
                    output = self.eatDots(gameState)   
        self.state = gameState
        self.updateposhistory(gameState)
        return output

    def updateposhistory(self, gameState):
        '''
        Update position history of the agent.
        '''
        if len(self.pos) < self.stuckThreshold:
            self.pos.append(gameState.getAgentPosition(self.index))
        else:
            self.pos.pop(0)
            self.pos.append(gameState.getAgentPosition(self.index))

        if self.ifChase(gameState):
            self.underchasing.append(1)
        else:
            self.underchasing.append(0)

    def ifStuck(self):
        '''
        Check if the agent is stuck. If stuck, return True.
        '''
        oddCount = 0
        evenCount = 0
        for i in range (0,self.stuckThreshold-1,2):
            if self.pos[i] == self.pos[i+2]:
                evenCount += 1
        for i in range (1,self.stuckThreshold-2,2):
            if self.pos[i] == self.pos[i+2]:
                oddCount += 1
        if evenCount == self.stuckThreshold // 2:
            if oddCount == self.stuckThreshold // 2 - 1: 
                # print("stuck")
                return True
        else:
            return False

    def ifLongChasing(self):
        '''
        Check if the agent is stuck by chasing.
        '''
        if self.underchasing[-1] ==1:
            res = next(i for i, j in enumerate(self.underchasing[::-1]) if j != 1)
            if res >= 20:
                print("Stuck by chasing!")
                return True
            else:
                return False
        else:
            return False
       
    def breaktie(self,gameState):
        '''
        Return a random action (excluding those will leads to dangerous positions) 
        if the agent is stuck. 
        '''
        safeAction = []
        dp = self.notGo2(gameState)
        legalActions = gameState.getLegalActions(self.index)
        x, y = gameState.getAgentPosition(self.index)
        for action in legalActions:
            dx, dy = Actions.directionToVector(action)
            nextPos = (int(x+dx), int(y+dy))
            if nextPos not in dp:
                if action != Directions.STOP:  
                    safeAction.append(action)
        if len(safeAction) != 0:
            # if self.safeBreakTie > 0:
            out = random.choice(safeAction)
                # self.safeBreakTie =- 1
            # else:
            #     out = random.choice(legalActions)
            #     self.safeBreakTie = 2
        else:
            out = random.choice(legalActions)
        return out

    def ifCatch(self, gameState):
        '''
        Return True if this agent is closer to opponents Pacman.
        Return False if it is further or it is a scared Ghost.
        谁近，谁去抓
        '''
        if len(self.getDots(gameState)) <= 2 and gameState.getAgentState(self.index).numCarrying == 0:
            return True
        if gameState.getAgentState(self.index).scaredTimer > 0:
            return False
        a = 0
        b = 0
        for i in self.enemyPIndex(gameState):
            a += self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(i).getPosition())
            b += self.getMazeDistance(gameState.getAgentState(self.anotherIndex(gameState)).getPosition(), gameState.getAgentState(i).getPosition())
        if a < b and a<=1:
            return True
        else:
            return False

    def catch(self, gameState):
        '''
        Return an action to chatch opponents' Pacman.
        捉对面的吃豆人
        '''
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
                path = self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [j], self.notGo2(gameState))
                if path is None:
                    continue
                if len(path) < b:
                    b = len(path)
                    a = path    
        if a is None or len(a) == 0:
            return Directions.STOP
        return a[0]

    def eatDots(self, gameState):
        '''
        Return an action to eat dots.
        Logistic is: go to the nearest food, if teammate goes to that position either, 
        change to chase the third nearest food.
        去最近的食物，如果队友也去，那么去第三近的
        '''
        if self.go_home:
            return self.goHome(gameState)
        if self.seduction==True:
            g_list=self.enemyGIndex(gameState)
            if g_list==None or len(g_list)==0:
                    self.seduction=False
            safe=True
            for i in self.enemyGIndex(gameState):
                if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(i).getPosition())<=4:
                    safe=False
            if safe==True:
                self.seduction=False
            
            if gameState.getAgentState(self.anotherIndex(gameState)).getPosition()[1]<=gameState.data.layout.height/2:
                if gameState.getAgentState(self.index).getPosition()==getMyLine(gameState, self.red)[len(getMyLine(gameState, self.red))-1]:
                    
                    self.seduction=False
                else:
                    top=getMyLine(gameState, self.red)[len(getMyLine(gameState, self.red))-1]
                    path= self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [top], self.notGo2(gameState))
                    if path is not None and len(path)>0:
                        return path[0]
            if gameState.getAgentState(self.anotherIndex(gameState)).getPosition()[1]>gameState.data.layout.height/2:
                if gameState.getAgentState(self.index).getPosition()==getMyLine(gameState, self.red)[0]:
                    self.seduction=False
                else:
                    bottom=getMyLine(gameState, self.red)[0]
                    path= self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [bottom], self.notGo2(gameState))
                    if path is not None and len(path)>0:
                        return path[0]

        ls = []
        if len(self.getDots(gameState)) > 15:
            dic = dict()
            for i in self.getDots(gameState):
                dic.update({i: self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), i)})
            ls1 = []
            for i in sorted(dic.items(), key=operator.itemgetter(1)):
                ls1.append(i[0])
            ls = ls1[0: 15]
        else:
            ls = self.getDots(gameState)
        dic3 = dict()
        for i in ls:
            if self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [i], self.notGo2(gameState)) is None:
                continue
            dic3.update({i: len(self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [i], self.notGo2(gameState)))})
        
        if len(dic3) == 0:
            self.seduction=True
            
            if gameState.getAgentState(self.anotherIndex(gameState)).getPosition()[1]<=gameState.data.layout.height/2:
                top=getMyLine(gameState, self.red)[len(getMyLine(gameState, self.red))-1]
                path= self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [top], self.notGo2(gameState))
                if path is not None and len(path)>0:
                    return path[0]
            else:
                bottom=getMyLine(gameState, self.red)[0]
                path= self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [bottom], self.notGo2(gameState))
                if path is not None and len(path)>0:
                    return path[0]
            return self.goHome(gameState)
        out = sorted(dic3.items(), key=operator.itemgetter(1))[0][0]
        out_val = sorted(dic3.items(), key=operator.itemgetter(1))[0][1]

        dic4 = dict()
        ls2 = []
        if len(self.getDots(gameState)) > 15:
            dic = dict()
            for i in self.getDots(gameState):
                dic.update({i: self.getMazeDistance(gameState.getAgentState(self.anotherIndex(gameState)).getPosition(), i)})
            ls1 = []
            for i in sorted(dic.items(), key=operator.itemgetter(1)):
                ls1.append(i[0])
            ls2 = ls1[0: 15]
        else:
            ls2 = self.getDots(gameState)

        for eat in ls2:
            path = self.aStarSearch(gameState, gameState.getAgentState(self.anotherIndex(gameState)).getPosition(), [eat], self.notGo2(gameState))
            if path is None:
                continue
            dic4.update({eat: len(path)})
        if len(dic4) != 0:
            out2 = sorted(dic4.items(), key=operator.itemgetter(1))[0][0]
            out2_val = sorted(dic4.items(), key=operator.itemgetter(1))[0][1]
            '''
            if out == out2 and out_val > out2_val and len(dic3) > int(len(self.my_dots)*2/3):
                out = sorted(dic3.items(), key=operator.itemgetter(1))[1][0]
            if out == out2 and out_val > out2_val and len(dic3) <= int(len(self.my_dots)*2/3): 
                out = sorted(dic3.items(), key=operator.itemgetter(1))[len(dic3)-1][0]
            
            '''
            dic5=dict()
            for i in range(min(len(dic3),len(dic4))):
                if sorted(dic3.items(), key=operator.itemgetter(1))[i][0] != sorted(dic4.items(), key=operator.itemgetter(1))[i][0]:
                    dic5.update({sorted(dic3.items(), key=operator.itemgetter(1))[i][0]:sorted(dic3.items(), key=operator.itemgetter(1))[i][1]})
                if sorted(dic3.items(), key=operator.itemgetter(1))[i][0] == sorted(dic4.items(), key=operator.itemgetter(1))[i][0] and sorted(dic3.items(), key=operator.itemgetter(1))[i][1] < sorted(dic4.items(), key=operator.itemgetter(1))[i][1]:
                    dic5.update({sorted(dic3.items(), key=operator.itemgetter(1))[i][0]:sorted(dic3.items(), key=operator.itemgetter(1))[i][1]})

            if len(dic5)!=0:
                out = sorted(dic5.items(), key=operator.itemgetter(1))[0][0]
            else:
                out = sorted(dic3.items(), key=operator.itemgetter(1))[0][0]
            # else:
            #     if self.index<self.anotherIndex(gameState):
            #         top=getMyLine(gameState, self.red)[len(getMyLine(gameState, self.red))-1]
            #         path = self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [top], self.notGo(gameState))
            #         if path is not None and len(path)>0:
            #             return path[0]
            #     else:
            #         bottom=getMyLine(gameState, self.red)[0]
            #         path = self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [bottom], self.notGo(gameState))
            #         if path is not None and len(path)>0:
            #             return path[0]
            #     return self.goHome(gameState)
            # if out == out2 and out_val > out2_val and len(dic3) >=2:
                
            #     out = sorted(dic3.items(), key=operator.itemgetter(1))[1][0]
            
            
            '''
            if len(self.getDots(gameState)) <= 3 and out_val > out2_val:
                if gameState.getAgentState(self.index).numCarrying > 0:
                    
                    return self.goHome(gameState)
                else:
                    
                    return self.catch(gameState)
            '''
        
        return self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [out], self.notGo2(gameState))[0]

    def goHome(self, gameState):
        '''
        Return an action that leads the agent home.
        回家
        '''
        if len(self.homeWay(gameState)) == 0:
            return self.luckyWay(gameState)
        return self.homeWay(gameState)[0]

    def ifChase(self, gameState):
        '''
        Return True if this agent is chasing by enemy's Ghost.
        正被追？
        '''
        for i in self.enemyGIndex2(self.state):
            for j in self.enemyGIndex2(gameState):
                if i == j:
                    if self.ifAtDeadRoute(gameState):
                        '''
                        if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(j).getPosition()) <= self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(i).getPosition()):

                            return True
                            '''
                    if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(j).getPosition()) <= self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(i).getPosition()) <= 4:
                        return True          
        return False

    def luckyWay(self, gameState):
        safeAction = []
        dp = self.notGo2(gameState)
        legalActions = gameState.getLegalActions(self.index)
        x, y = gameState.getAgentPosition(self.index)
        for action in legalActions:
            dx, dy = Actions.directionToVector(action)
            nextPos = (int(x+dx), int(y+dy))
            if nextPos not in dp:  
                safeAction.append(action)
        if len(safeAction) != 0:
            # if self.safeBreakTie > 0:
            out = random.choice(safeAction)
                # self.safeBreakTie =- 1
            # else:
            #     out = random.choice(legalActions)
            #     self.safeBreakTie = 2
        else:
            out = random.choice(legalActions)
        return out

    def CapOrHome(self, gameState):
        '''
        Return action to go home or to chase capsule.
        被追去吃药丸或回家
        '''
        way = self.homeWay(gameState)
        # when finish eating 18 dots or time is up, go home
        if len(way) > 0 and ((len(self.getDots(gameState)) <= 2) or(gameState.data.timeleft < 80 and gameState.getAgentState(self.index).numCarrying > 0) or (len(way) <= 5 and gameState.getAgentState(self.index).numCarrying >= 4 and not self.oppoPac(gameState))):
            return way[0]
        a = None
        b = 999999  
        for i in self.getCapsules(gameState):
            path = self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [i], self.notGo2(gameState))
            if path is None:
                continue
            if len(path) < b:
                b = len(path)
                a = i
        if a is not None:
            return self.aStarSearch(gameState, gameState.getAgentState(self.index).getPosition(), [a], self.notGo2(gameState))[0]
        if gameState.getAgentState(self.index).numCarrying ==0:
            return self.eatDots2(gameState)
        else:
            if len(way) == 0:
                return self.luckyWay(gameState)
            else:
                return way[0]

    def ifGoHome(self, gameState):
        '''
        Judge if go home or not.
        是否回家
        '''
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
        '''
        Return True if in dead route on opponents half side of map, otherwise return False.
        判断是否在死胡同
        '''
        ls = list(self.spl[2])+list(self.spl[3])
        if gameState.getAgentState(self.index).getPosition() in ls:
            return True
        else:
            return False

    def aStarSearch(self, gameState, start, goal, lis):
        '''
        A star search.
        Use Maze distance as heuristic.
        Where lis is a list of dangerous places we should not go.
        '''
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
        '''
        Return a list of positions of initial food our agents supposed to defend.
        我方初始豆子位置
        '''
        return self.getFoodYouAreDefending(gameState).asList() + self.getCapsulesYouAreDefending(gameState)

    def oppoPac(self, gameState):
        '''
        Return True if all of opponent's agents are pacman.
        对方全是Pacman？
        '''
        return gameState.getAgentState(self.getOpponents(gameState)[0]).isPacman and gameState.getAgentState(self.getOpponents(gameState)[1]).isPacman

    def enemyPosition(self, gameState):
        '''
        Return a list of opponent agents indices if we can see its position.
        哪个对方的agent在我方视野范围内
        '''
        lis = []
        if gameState.getAgentPosition(self.getOpponents(gameState)[0]) is not None:
            lis.append(self.getOpponents(gameState)[0])
        if gameState.getAgentPosition(self.getOpponents(gameState)[1]) is not None:
            lis.append(self.getOpponents(gameState)[1])
        return lis

    def enemyGIndex(self, gameState):
        '''
        Return a list of opponent agents indices if it is nearby us and 
        it is ghost and it is not scared (or scared time almost done).
        In a word, which is is a threat to our agents.
        附近的有威胁的Ghost敌人的index
        '''
        output = []
        for i in self.enemyPosition(gameState):
            if not gameState.getAgentState(i).isPacman and gameState.getAgentState(i).scaredTimer<=5:
                output.append(i)
        return output

    def enemyGIndex2(self, gameState):
        '''
        Return a list of opponent agents indices if it is nearby us and 
        it is ghost and it is not scared (or scared time almost done).
        In a word, which is is a threat to our agents.
        附近的有威胁的Ghost敌人的index
        '''
        output = []
        for i in self.enemyPosition(gameState):
            if not gameState.getAgentState(i).isPacman and gameState.getAgentState(i).scaredTimer<=15:
                output.append(i)
        return output

    def enemyGPosition(self, gameState):
        '''
        Return a list of opponent agents positions if it is nearby us and 
        it is ghost and it is not scared (or scared time almost done).
        In a word, which is is a threat to our agents.
        附近的有威胁的Ghost敌人的位置
        '''
        out = []
        for i in self.enemyGIndex(gameState):
            out.append(gameState.getAgentState(i).getPosition())
        return out

    def enemyPPosition(self, gameState):
        '''
        Return a list of opponent agents positions if it is nearby us and it is Pacman.
        附近的Pacman敌人的位置
        '''
        out = []
        for i in self.enemyPIndex(gameState):
            out.append(gameState.getAgentState(i).getPosition())
        return out

    def enemyPIndex(self, gameState):
        '''
        Return a list of opponent agents indices if it is nearby us and it is Pacman.
        附近的Pacman敌人的index
        '''
        output = []
        for i in self.enemyPosition(gameState):
            if gameState.getAgentState(i).isPacman:
                output.append(i)
        return output

    def notGo(self, gameState):
        '''
        Return a list of dangerous positions for us in this game state, 
        including positions nearby Ghost enemies and dear route.
        We should avoid actions go to these positions.
        不要去的位置（包括敌人附近和死胡同）
        '''
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
        
        for j in self.enemyPPosition(gameState):
            if self.red and j in getMyLine(gameState, self.red):
                output.append((int(j[0] + 1), int(j[1])))
            if not self.red and j in getMyLine(gameState, self.red):
                output.append((int(j[0] - 1), int(j[1])))
            '''
            if self.getMazeDistance(j, gameState.getAgentState(self.index).getPosition())<=5:
                output=output+list(self.spl[2])
                output=output+list(self.spl[3])
            '''
        
        if gameState.getAgentState(self.index).scaredTimer > 0:
            output=output+self.enemyPPosition(gameState)
            for k in self.enemyPPosition(gameState):
                output=output+list(getAroundPositions(gameState, k))
        return output

    def notGo2(self, gameState):
        '''
        Return a list of dangerous positions for us in this game state.
        We should avoid actions go to these positions.
        This function not including dead ends or corrider leading to a dead ends as dangerous place.
        不要去的位置（包括敌人附近，不包括死胡同）
        '''
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
        '''
        Return index of another agent of ours.
        友军的index  
        '''
        if self.index == self.getTeam(gameState)[0]:
            index = self.getTeam(gameState)[1]
        else:
            index = self.getTeam(gameState)[0]
        return index

    def homeWay(self, gameState):
        '''
        Return a list of actions of shortest way to go back to our side to unload food.
        最近的回家的路
        '''
        dp = self.notGo2(gameState)
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

    def getDots(self, gameState):
        '''
        Return a list of positions of remained food our agents supposed to eat.
        剩余的本方食物
        '''
        return self.getFood(gameState).asList()
    
    def getMinDistToFood(self, gameState):
        myPos = gameState.getAgentPosition(self.index)
        if len(self.getFood(gameState).asList())==0:
            return 0
        else:
            return min([self.getMazeDistance(myPos,f) for f in self.getFood(gameState).asList()])

##########################
# Upper Confidence Trees #
##########################

class Node(object):

    def __init__(self, gameState, agent, action, parentNode, ghostPos, borderline):
        self.parentNode = parentNode
        self.action = action
        if parentNode == None:
            self.deepth = 0
        else:
            self.deepth = parentNode.deepth + 1

        self.child = []
        self.v_times = 1
        self.q_value = 0.0

        self.gameState = gameState.deepCopy()
        self.ghostPos = ghostPos
        self.legalActions = gameState.getLegalActions(agent.index)
        self.illegalActions = []
        self.legalActions.remove('Stop')

        self.legalActions = list(set(self.legalActions)-set(self.illegalActions))

        self.unexploredActions = self.legalActions[:]
        self.borderline = borderline
        
        self.agent = agent
        self.E = 0.9
    
def getBestChild(node):
    bestScore = -99999
    bestChild = None
    for n in node.child:
        score = n.q_value/n.v_times
        if score > bestScore:
            bestScore = score
            bestChild = n
    return bestChild
    
def getExpandedNode(node):
    if node.deepth >= 10:
        return node

    if node.unexploredActions != []:
        action = node.unexploredActions.pop()
        tempGameState = node.gameState.deepCopy()
        nextGameState = tempGameState.generateSuccessor(node.agent.index,action)
        childNode = Node(nextGameState,node.agent,action,node,node.ghostPos,node.borderline)
        node.child.append(childNode)
        return childNode
    
    if util.flipCoin(node.E): # E-greedy 
        nextBestNode = getBestChild(node)
    else:
        nextBestNode = random.choice(node.child)
    return getExpandedNode(nextBestNode)

def getReward(node):
    nowPos = node.gameState.getAgentPosition(node.agent.index)
    if nowPos == node.gameState.getInitialAgentPosition(node.agent.index):
        return -len(node.agent.getCapsules(node.gameState))*200-1000
    
    dis_to_ghost = min(node.agent.getMazeDistance(nowPos,ghost_pos) for ghost_pos in node.ghostPos)
    if dis_to_ghost <= node.deepth-1:
        return -len(node.agent.getCapsules(node.gameState))*200-100

    value = getFeaturesAttack(node.agent,node)*getWeight()
    return value
    
def backpropagation(node,reward):
    node.v_times += 1
    node.q_value += reward
    if node.parentNode != None:
        backpropagation(node.parentNode,reward)

def MCTS(node):
    timeLimit = 0.5
    start = time.time()
    while(time.time()-start < timeLimit):
        nodeExpanded = getExpandedNode(node) #selection and expand
        reward = getReward(Simulation(nodeExpanded))
        backpropagation(nodeExpanded,reward)
    return getBestChild(node).action

def Simulation(node):
    for i in range(5):
        if node.unexploredActions != []:
            action = node.unexploredActions.pop()
            tempGameState = node.gameState.deepCopy()
            nextGameState = tempGameState.generateSuccessor(node.agent.index,action)
            childNode = Node(nextGameState,node.agent,action,node,node.ghostPos,node.borderline)
            node.child.append(childNode)
            if len(node.child)==0:
                return node
            else:
                node = random.choice(node.child)
    return node

def getFeaturesAttack(agent,node):
    """
    Returns a counter of features for the state
    """
    gameState = node.gameState
    lastGameState = node.parentNode.gameState
    features = util.Counter()

    features['getFood'] = gameState.getAgentState(agent.index).numCarrying - lastGameState.getAgentState(agent.index).numCarrying

    features['minDistToFood'] = agent.getMinDistToFood(gameState)

    features['capsuleRemain'] = len(agent.getCapsules(gameState))

    return features

def getWeight():
    return {'minDistToFood':-1,'getFood':10, 'capsuleRemain': -200}


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