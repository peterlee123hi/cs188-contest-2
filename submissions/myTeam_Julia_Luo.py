"""
Students' Names: Julia Luo, Ellen Luo
Contest Number: 2
Description of Bot: We used a reflex bot for this contest, with features and weights. We split into Offensive and
Defensive bots, each with their own features and weights. We have our offensive bot target only 1 food at first, and
switch to defence as long as we are winning in points. If not, it switches back to offense to collect |score| + 1 points
to ensure that we are ahead. The features for the offensive bot include distance to closest food, distance to closest ghost,
distance to border, and number of food collected. The features for the defensive bot are just distance to the closest opponent
and the number of opponent pacman on our side.
"""
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
# 
from __future__ import division
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
##########
# Search #
##########
def nullHeuristic(state, problem=None):
    return 0
def aStarSearch(problem, heuristic=nullHeuristic):
    priorityFunction = lambda node: node.cost + heuristic(node.state, problem)
    fringe = util.PriorityQueueWithFunction(priorityFunction)
    updateCost = lambda x, y: None
    return genericSearch(problem, fringe, updateCost)
def depthFirstSearch(problem):
    fringe = util.Stack()
    updateCost = lambda x, y: None
    return genericSearch(problem, fringe, updateCost)
def genericSearch(problem, fringe, updateCost):
    closed = set()
    startNode = Node(problem.getStartState())
    fringe.push(startNode)
    while not fringe.isEmpty():
      node = fringe.pop()
      if problem.isGoalState(node.state):
          actionList = getActionList(node)
          return actionList
      if node.state not in closed:
          closed.add(node.state)
          for (nextState, action, stepCost) in problem.getSuccessors(node.state):
              if nextState not in closed:
                  nextNode = Node(nextState, action, node.cost + stepCost, node)
                  fringe.push(nextNode)
    return []
class Node:
    def __init__(self, state, action=None, cost=0, prev=None):
        self.state = state
        self.action = action
        self.cost = cost
        self.prev = prev
def getActionList(node):
    lst = []
    curr = node
    while curr.action:
        lst.append(curr.action)
        curr = curr.prev
    return lst[::-1]
class SearchProblem:
  def __init__(self, startState, agent):
    self.startState = startState
    self.agent = agent
    self.goal = None
  def getStartState(self):
    return self.startState
  def isGoalState(self, state):
    pos = state.getAgentPosition(self.agent.index)
    return pos == self.goal
  def getSuccessors(self, state):
    actions = state.getLegalActions(self.agent.index)
    successors = [(self.agent.getSuccessor(state, a), a, 1) for a in actions]
    return successors
MAZE_HEIGHT = 14
MAZE_WIDTH = 30
def invalidPos(gameState, x, y):
    if x < 0 or y < 0 or x >= MAZE_WIDTH or y >= MAZE_HEIGHT:
        return True
    return gameState.hasWall(x, y)
#################
# Team creation #
#################
def createTeam(firstIndex, secondIndex, isRed,
               first = 'SmartAgent', second = 'SmartAgent'):
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
class SmartAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        startPos = gameState.getAgentPosition(self.index)
        self.start = startPos
        mid = (gameState.data.layout.width / 2) - 1
        if startPos[0] <= mid:
            self.boundary = mid
        elif startPos[0] > mid:
            self.debugDraw([(mid + 1, 0)], [255, 255, 255])
            self.debugDraw([(mid, 0)], [255, 255, 255])
            self.boundary = mid + 1
        self.startPos = startPos
        if self.index == self.getTeam(gameState)[0]:
            self.defense = False
            self.numToCollect = 1
            self.foodBeforeCollect = len(self.getFood(gameState).asList())
            self.offensiveFeatures(gameState)
        else:
            self.defense = True
            self.defensiveFeatures(gameState)
    def offensiveFeatures(self, gameState):
        def closestGhost(self, state, action):
            dist, closest = min(
                [(self.getMazeDistance(state.getAgentPosition(i), 
                    state.getAgentPosition(self.index)), state.getAgentPosition(i)) for i in self.getOpponents(state)], 
                key=lambda x: x[0])
            if dist == 0:
                return 1
            return 0 if (dist > 10 or self.onSameSide(closest)) else 1/(dist + 1)
        def distToFood(self, state, action):
            food = self.getFood(state).asList()
            if len(food) < self.foodBeforeCollect - self.numToCollect:
                return 0
            return 1/(min([self.getMazeDistance(state.getAgentPosition(self.index), f) for f in food]) + 1)
        def numFoodCollected(self, state, action):
            food = self.getFood(state).asList()
            if len(food) < self.foodBeforeCollect - self.numToCollect:
                return 0
            return self.foodBeforeCollect - len(food)
        def distToBorder(self, state, action):
            boundary = self.findClosestBoundary(state)
            return 1/(self.getMazeDistance(state.getAgentPosition(self.index), boundary) + 1)
        #distToBorder = lambda self, state, action: 1/(abs(state.getAgentPosition(self.index)[0] - self.boundary) + 1)
        #numFoodCollected = lambda self, state, action: self.startNumFood - len(self.getFood(state).asList())
        self.features = {'closestGhost': closestGhost, 'distToBorder': distToBorder, 'distToFood': distToFood, 'numFoodCollected': numFoodCollected}
        self.weights = {'closestGhost': -15, 'distToBorder': 0.1, 'distToFood': 10, 'numFoodCollected': 10}
    def defensiveFeatures(self, gameState):
        def closestPacman(self, state, action):
            opponentPos = [state.getAgentPosition(i) for i in self.getOpponents(state)]
            opponentPacman = [pos for pos in opponentPos if self.onSameSide(pos)]
            if not opponentPacman:
                opponentPacman = opponentPos
            dist, closest = min([(self.getMazeDistance(pos, state.getAgentPosition(self.index)), pos) for pos in opponentPacman])
            return 0 if not self.onSameSide(state.getAgentPosition(self.index)) else 1/(dist + 1)
        def numPacmanOnSide(self, state, action):
            onSide = [self.onSameSide(state.getAgentPosition(i)) for i in self.getOpponents(state)]
            return onSide.count(True)
        #numFoodCollected = lambda self, state, action: len(self.getFoodYouAreDefending(state).asList())
        self.features = {'closestPacman': closestPacman, 'numPacmanOnSide': numPacmanOnSide}
        self.weights = {'closestPacman': 1, 'numPacmanOnSide': -4}
    def chooseAction(self, state):
        if self.index == self.getTeam(state)[0]:
            if (self.getScore(state) <= 0 and self.defense) or (
                    not self.defense and state.getAgentPosition(self.index) == self.start):
                self.defense = False
                self.offensiveFeatures(state)
                self.numToCollect = abs(self.getScore(state)) + 1
                self.foodBeforeCollect = len(self.getFood(state).asList())
            elif self.getScore(state) > 0 and not self.defense:
                self.defense = True
                self.defensiveFeatures(state)
            elif not self.defense and self.foodBeforeCollect - len(self.getFood(state).asList()) >= self.numToCollect:
                self.weights['distToBorder'] = 10
                self.weights['distToFood'] = 0
                self.weights['numFoodCollected'] = 0
        return self.computeActionFromQValues(state)
    def getQValue(self, state, action):
        qVal = 0
        for f in self.features:
            qVal += self.features[f](self, state, action) * self.weights[f]
        return qVal
    def computeValueFromQValues(self, state):
        actions = state.getLegalActions(self.index)
        if not actions:
            return 0
        maxQ = -99999
        for a in actions:
            nextState = state.generateSuccessor(self.index, a)
            for nextA in nextState.getLegalActions(self.index):
                nextnextState = nextState.generateSuccessor(self.index, nextA)
                maxQ = max(self.getQValue(nextnextState, nextA), maxQ)
        return maxQ
    def computeActionFromQValues(self, state): 
        if not state.getLegalActions(self.index):
            return None
        maxQ = self.computeValueFromQValues(state)
        pos = state.getAgentPosition(self.index)
        lst = []
        for a in state.getLegalActions(self.index):
            nextState = state.generateSuccessor(self.index, a)
            for nextA in nextState.getLegalActions(self.index):
                nextnextState = nextState.generateSuccessor(self.index, nextA)
                if self.getQValue(nextnextState, nextA) == maxQ:
                    lst.append(a)
        if self.defense and 'Stop' in lst:
            return 'Stop'
        return random.choice(lst)
    def onSameSide(self, pos):
        return (self.startPos[0] <= 15 and pos[0] <= self.boundary) or (self.startPos[0] >= 16 and pos[0] >= self.boundary)
    def findClosestBoundary(self, gameState):
        walls = gameState.getWalls().asList()
        pos = gameState.getAgentPosition(self.index)
        candidates = [(self.boundary, i) for i in range(1, MAZE_HEIGHT + 1) if (self.boundary, i) not in walls]
        distances = [(self.getMazeDistance(pos, p), p) for p in candidates]
        minCand = min(distances, key=lambda x: x[0])
        return minCand[1]
    """
    def capsuleSearch(self, startPos, gameState):
        paths = [([startPos], 0)]
        finalPaths = []
        for t in range(40):
            newPaths = []
            for path, score in paths:
                x, y = path[-1]
                x2, y2 = -1, -1
                if len(path) > 1:
                    x2, y2 = path[-2]
                successors = [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]
                for newX, newY in successors:
                    if invalidPos(gameState, newX, newY):
                        continue
                    if newX == x2 and newY == y2:
                        continue
                    newScore = score
                    if gameState.hasFood(newX, newY):
                        newScore += 1
                    if newX == self.boundary:
                        finalPaths.append((path + [(newX, newY)], newScore))
                    elif t > 0 and t % 10 == 0 and newScore == 0:
                        continue
                    else:
                        newPaths.append((path + [(newX, newY)], newScore))
            paths = newPaths 
        path = max(finalPaths, key=lambda x: x[1])
        actions = []
        for i in range(1, len(path)):
            x1, y1 = path[i-1]
            x2, y2 = path[i]
            if x2 == x1 - 1 and y2 == y1:
                actions.append('West')
            elif x2 == x1 and y2 == y1 - 1:
                actions.append('South')
            elif x2 == x1 + 1 and y2 == y1:
                actions.append('East')
            elif x2 == x1 and y2 == y1 + 1:
                actions.append('North')
            else:
                actions.append('Error')
        return actions
        """
class LearningAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState) 
        startPos = gameState.getAgentPosition(self.index)
        if startPos[0] <= 15:
          self.boundary = 16
        elif startPos[0] > 15:
          self.boundary = 17
        self.prevState = None
        self.prevAction = None
        self.weights = {}
        self.epsilon = 0.1
        self.discount = 0.9
        self.alpha = 0.5
        self.defense = False
        # Set self.features - f(state, action)
        # Read in current weights from external file/persisted state 
    def chooseAction(self, state):
        if self.prevState:
            # Set reward - what should this be?
            prevScore = self.getScore(self.prevState)
            currScore = self.getScore(state)
            if self.defense:
                prevFood = self.getFoodYouAreDefending(self.prevState).asList()
                currFood = self.getFoodYouAreDefending(state).asList()
                if currScore < prevScore:
                    reward = len(currFood) - len(prevFood) + currScore - prevScore
                else:
                    reward = len(currFood) - len(prevFood)
            else:
                prevFood = self.getFood(self.prevState).asList()
                currFood = self.getFood(state).asList()
                if currScore > prevScore:
                    reward = len(currFood) - len(prevFood) + currScore - prevScore
                else:
                    reward =  len(currFood) - len(prevFood)
            self.update(self.prevState, self.prevAction, state, reward)
        legalActions = state.getLegalActions(self.index)
        p = random.uniform(0, 1)
        #if p < self.epsilon:
        if p < 0:
            action = random.choice(legalActions)
        else:
            action = self.computeActionFromQValues(state)
        self.prevAction = action
        self.prevState = state
        return action
    def getQValue(self, state, action):  
        qVal = 0
        for f in self.features:
            qVal += self.features[f](self, state, action) * self.weights[f]
        return qVal
    def computeValueFromQValues(self, state):
        actions = state.getLegalActions(self.index)
        if not actions:
            return 0
        maxQ = -999999999
        for a in actions:
            nextState = state.generateSuccessor(self.index, a)
            #xPos = nextState.getAgentPosition(self.index)
            #if not (self.defense and ((self.boundary == 16 and xPos > 16) or (self.boundary == 17 and xPos < 17))):
            maxQ = max(self.getQValue(state, a), maxQ)
        return maxQ
    def computeActionFromQValues(self, state): 
        if not state.getLegalActions(self.index):
            return None
        maxQ = self.computeValueFromQValues(state)
        lst = []
        for a in state.getLegalActions(self.index):
            if self.getQValue(state, a) == maxQ:
                lst.append(a)
        return random.choice(lst)
    def update(self, state, action, nextState, reward):
        maxQ = self.computeValueFromQValues(nextState)
        diff = (reward + self.discount * maxQ) - self.getQValue(state, action)
        for f in self.features:
            self.weights[f] += self.alpha * diff * self.features[f](self, state, action)
        # Write weights to external file/persisted state
        if self.defense:
            f = open('defense.txt', 'w')
            for key, value in self.weights.items():
                f.write(key + ' ' + str(value) + '\n')
        else:
            f = open('offense.txt', 'w')
            for key, value in self.weights.items():
                f.write(key + ' ' + str(value) + '\n')
    def onSameSide(self, pos):
        return (self.boundary == 16 and pos[0] <= 16) or (self.boundary == 17 and pos[0] >= 17)
class OffensiveLearningAgent(LearningAgent):
    def registerInitialState(self, gameState): 
        LearningAgent.registerInitialState(self, gameState)
        def closestGhost(self, state, action):
            dist, closest = min(
                [(self.getMazeDistance(state.getAgentPosition(i), 
                    state.getAgentPosition(self.index)), state.getAgentPosition(i)) for i in self.getOpponents(state)], 
                key=lambda x: x[0])
            return 0 if (dist < 10 or self.onSameSide(closest)) else 1/(dist + 1)
        def distToFood(self, state, action):
            food = self.getFood(state).asList()
            if len(food) <= 2:
                return 0
            return 1/(min([self.getMazeDistance(state.getAgentPosition(self.index), f) for f in food]) + 1)
        distToBorder = lambda self, state, action: 1/(abs(state.getAgentPosition(self.index)[0] - self.boundary) + 1)
        self.features = {'closestGhost': closestGhost, 'distToBorder': distToBorder, 'distToFood': distToFood}
        f = open('offense.txt', 'r')
        text = list(f)
        for line in text:
            weight = line.split()
            self.weights[weight[0]] = float(weight[1])
        f.close()
class DefensiveLearningAgent(LearningAgent):
    def registerInitialState(self, gameState): 
        LearningAgent.registerInitialState(self, gameState)
        self.defense = True
        closestOpponent = lambda self, state, action: 1/(min(
            [self.getMazeDistance(state.getAgentPosition(i), state.getAgentPosition(self.index)) for i in self.getOpponents(state)]) + 1)
        opponentToBorder = lambda self, state, action: 1/(min([abs(state.getAgentPosition(i)[0] - self.boundary) for i in self.getOpponents(state)]) + 1)
        #numFoodCollected = lambda self, state, action: len(self.getFoodYouAreDefending(state).asList())
        self.features = {'closestOpponent': closestOpponent, 'opponentToBorder': opponentToBorder}
        f = open('defense.txt', 'r')
        text = list(f)
        for line in text:
            weight = line.split()
            self.weights[weight[0]] = float(weight[1])
        f.close()
"""
MAZE_HEIGHT = 14
MAZE_WIDTH = 30
threats = []
targets = []
class SearchAgent(CaptureAgent):
    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)
        startPos = gameState.getAgentPosition(self.index)
        if startPos[0] <= 15:
          boundary = 16
        elif startPos[0] > 15:
          boundary = 17
        walls = gameState.getWalls().asList()
        self.chokepoints = [(boundary, i) for i in range(1, MAZE_HEIGHT + 1) if (boundary, i) not in walls]
        self.target = None
        self.capsulesToDefend = self.getCapsulesYouAreDefending(gameState)
        self.targetCapsules = self.getCapsules(gameState)
        self.problem = SearchProblem(gameState, self)        
    def chooseAction(self, gameState):
        oppIndices = self.getOpponents(gameState)
        oppPos = [gameState.getAgentPosition(i) for i in oppIndices]
        oppDist = [min([self.getMazeDistance(pos, cp) for cp in chokepoints]) for pos in oppPos]
        for i in range(len(oppIndices)):
            if oppDist[i] < 5 and oppIndices[i] not in threats:
                threats.append(oppIndices[i])
            elif oppDist[i] >= 5 and oppIndices[i] in threats:
                threats.remove(oppIndices[i])
        if len(threats) > len(targets) and not self.target:
            for t in threats:
                if t not in targets:
                    self.target = t
                    targets.append(t)
            return defensiveStrategy(gameState)
        if self.target and self.target not in threats:
            self.target = None
            return offensiveStrategy(gameState)
        if self.target:
            return defensiveStrategy(gameState)
        return offensiveStrategy(gameState)
    def defensiveStrategy(self, gameState):
        pos = gameState.getAgentPosition(self.target) 
        cp = min(self.chokepoints, key=lambda x: self.getMazeDistance(pos, x))
    def offensiveStrategy(self, gameState):
        return
"""
