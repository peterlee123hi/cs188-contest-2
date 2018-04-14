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

"""
This submission is by Joshua Yurtsever and Luke Dzwonczyk. We use minimax and features
such as the number of pelets, dead ends, number of power pelets, and the distance
from ghosts for our AI to make decisions.
"""
import random
import sys
import time
from util import manhattanDistance

from captureAgents import CaptureAgent


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefenseAgent', second = 'OffenseAgent'):
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

class DefenseAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
  def __init__(self, index, timeForComputing = .1):
      CaptureAgent.__init__(self, index, timeForComputing)
      self.steps = 0
      self.defense = True
      self.begintime = time.time()

  def evaluationFunction(self, gameState):
      enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      myState = gameState.getAgentState(self.index)
      myPos = myState.getPosition()

      closestFoodDist = min(map(lambda x: self.getMazeDistance(x, myPos), self.getFood(gameState).asList()))
      if myState.isPacman:
         return -5
      if invaders:
          invaderDist = min([self.getMazeDistance(myPos, e.getPosition()) for e in invaders if e.getPosition() != None])
          if invaderDist == 0:
              return 10
          else:
              enemyScore = -invaderDist
      else:
          enemyScore = 20 - closestFoodDist
      return foodCount(self.getFoodYouAreDefending(gameState)) + enemyScore + self.getScore(gameState)

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


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)
    self.begintime = time.time()
    '''
    Defense Agent focuses on eating enemy pacman in its zone as long
    as it is not scared.
    '''
    depth = 2
    defense = [self.index]
    agentInds = defense + [i for i in self.getOpponents(gameState) if gameState.getAgentState(i).isPacman and
                                gameState.getAgentState(i).getPosition() != None]
    numAgents = len(agentInds)
    def calcWithPrune(gameState, depth, k, alpha, beta):
        if depth == 0 or (time.time() - self.begintime > self.timeForComputing and k == 0):
            actions = gameState.getLegalActions(self.index)
            return self.evaluationFunction(gameState), random.choice(actions)
        acts = gameState.getLegalActions(agentInds[k])
        nextk = (k + 1) % numAgents
        bestAction = None
        if not nextk:
            depth -= 1
        if k >= len(defense): #minimizer
            v = sys.maxint
            for act in acts:
                next = calcWithPrune(gameState.generateSuccessor(agentInds[k], act),
                                     depth, nextk, alpha, beta)[0]
                if next < v:
                    v = next
                    bestAction = act
                if v < alpha:
                    return v, act
                beta = min(beta, v)
        else: #maximizer
            v = -sys.maxint
            for act in acts:
                child = calcWithPrune(gameState.generateSuccessor(agentInds[k], act),
                                      depth, nextk, alpha, beta)[0]
                if child > v:
                    v = child
                    bestAction = act
                if v > beta:
                    return v, act
                alpha = max(alpha, v)
        return v, bestAction

    return calcWithPrune(gameState, depth, 0, -sys.maxint, sys.maxint)[1]





class OffenseAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
  def __init__(self, index, timeForComputing = .1):
      CaptureAgent.__init__(self, index, timeForComputing)
      self.steps = 0
      self.defense = False
      self.base = None
      self.begintime = time.time()

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
    self.base = gameState.getAgentPosition(self.index)
    self.calibrate = 0
    self.followedCount = 0

  def chooseAction(self, gameState):
    """
    Finds the best action using minimax
    """
    self.begintime = time.time()
    if self.followed(gameState):
        self.followedCount += 1
    else:
        self.followedCount = 0
    if gameState.getAgentState(self.index).numCarrying - self.calibrate >= 5 or self.followedCount > 3:
        if not gameState.getAgentState(self.index).isPacman:
            self.calibrate = gameState.getAgentState(self.index).numCarrying
        actions = gameState.getLegalActions(self.index)
        result = None
        best = -sys.maxint
        for act in actions:
            if act == 'Stop':
                continue
            if self.backeval(gameState.generateSuccessor(self.index, act)) > best:
                result = act
                best = self.backeval(gameState.generateSuccessor(self.index, act))
        return result

    depth = 2
    agentInds = [self.index] + [i for i in self.getOpponents(gameState) if not gameState.getAgentState(i).isPacman and
                                gameState.getAgentState(i).getPosition() != None]
    numAgents = len(agentInds)
    def calcWithPrune(gameState, depth, k, alpha, beta):
        if depth == 0 or (time.time() - self.begintime > self.timeForComputing and k == 0):
            actions = gameState.getLegalActions(self.index)
            return self.evaluationFunction(gameState), random.choice(actions)
        acts = gameState.getLegalActions(agentInds[k])
        nextk = (k + 1) % numAgents
        bestAction = None
        if not nextk:
            depth -= 1
        if k != 0: #minimizer
            v = sys.maxint
            for act in acts:
                next = calcWithPrune(gameState.generateSuccessor(agentInds[k], act),
                                     depth, nextk, alpha, beta)[0]
                if next < v:
                    v = next
                    bestAction = act
                if v < alpha:
                    return v, act
                beta = min(beta, v)
        else: #maximizer
            v = -sys.maxint
            for act in acts:
                if act == 'Stop':
                    continue
                child = calcWithPrune(gameState.generateSuccessor(agentInds[k], act),
                                      depth, nextk, alpha, beta)[0]
                if child > v:
                    v = child
                    bestAction = act
                if v > beta:
                    return v, act
                alpha = max(alpha, v)
        return v, bestAction

    return calcWithPrune(gameState, depth, 0, -sys.maxint, sys.maxint)[1]
  def followed(self, gameState):
      enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      newScaredTimes = [g.scaredTimer for g in ghosts]
      newGhostPositions = [g.getPosition() for g in ghosts]
      myState = gameState.getAgentState(self.index)
      myPos = myState.getPosition()
      if ghosts:
          closestGhost = newGhostPositions[0]
          for ghostPos in newGhostPositions:
              if self.getMazeDistance(ghostPos, myPos) < self.getMazeDistance(closestGhost, myPos):
                  closestGhost = ghostPos
          return self.getMazeDistance(closestGhost, myPos) < 2
      return False

  def backeval(self, gameState):
      enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      newScaredTimes = [g.scaredTimer for g in ghosts]
      newGhostPositions = [g.getPosition() for g in ghosts]
      myState = gameState.getAgentState(self.index)
      myPos = myState.getPosition()
      lenCaps = len(self.getCapsules(gameState))
      if ghosts:
          backDist = self.getMazeDistance(myPos, self.base)
          closestGhost = newGhostPositions[0]  # tuple
          for ghostPos in newGhostPositions:
              if self.getMazeDistance(ghostPos, myPos) < self.getMazeDistance(closestGhost, myPos):
                  closestGhost = ghostPos
          if self.getMazeDistance(closestGhost, myPos) == 0:
              return -100000000
          if newScaredTimes[newGhostPositions.index(closestGhost)] < 6:
              ghostWeight = .2
              ghostScore = self.getMazeDistance(closestGhost, myPos)
              return ghostWeight * ghostScore / (backDist + 1) - 2*backDist -  100*lenCaps
      return self.evaluationFunction(gameState)
  def evaluationFunction(self, gameState):
    myState = gameState.getAgentState(self.index)
    myPos = myState.getPosition()
    myFood = self.getFood(gameState)
    if not myState.isPacman:
        pac = -5
    else:
        pac = 0
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    GhostStates = ghosts
    newScaredTimes = [ghostState.scaredTimer for ghostState in GhostStates]

    closestFoodDist = min(map(lambda x: self.getMazeDistance(x, myPos), myFood.asList()))
    newGhostPositions = [g.getPosition() for g in ghosts]

    closeFoodScore = 1 / float(closestFoodDist) if not myFood[int(myPos[0])][int(myPos[1])] else 20
    lenCaps = len(self.getCapsules(gameState))

    if self.getCapsules(gameState):
        closestCapDist = min(map(lambda x: self.getMazeDistance(x, myPos), self.getCapsules(gameState)))
        capScore = 1/float(closestCapDist)
    else:
        closestCapDist = 0
        capScore = 0
    if GhostStates:
        closestGhost = newGhostPositions[0]  # tuple
        for ghostPos in newGhostPositions:
          if self.getMazeDistance(ghostPos, myPos) < self.getMazeDistance(closestGhost, myPos):
            closestGhost = ghostPos
        if self.getMazeDistance(closestGhost, myPos) == 0:
            return -100000000
        if self.getMazeDistance(closestGhost, myPos) < 3 and deadEnd(gameState, myPos):
                return -1000
        if newScaredTimes[newGhostPositions.index(closestGhost)] == 0:
            ghostWeight = .2
            if self.followed(gameState):
                ghostWeight = .7
            ghostScore = self.getMazeDistance(closestGhost, myPos)
            return self.getScore(gameState) + ghostWeight * ghostScore / (
                closestFoodDist + 1) - foodCount(self.getFood(gameState)) + 3*closeFoodScore + pac - 100*lenCaps
    return closeFoodScore - 5*foodCount(myFood)

def deadEnd(gameState, myPos):
    combinations = [[(myPos[0], myPos[1] + 1), (myPos[0] + 1, myPos[1]), (myPos[0], myPos[1] - 1)],
                    [(myPos[0], myPos[1] + 1), (myPos[0] - 1, myPos[1]), (myPos[0], myPos[1] - 1)],
                    [(myPos[0] - 1, myPos[1]), (myPos[0], myPos[1] + 1), (myPos[0], myPos[1] - 1)],
                    [(myPos[0] + 1, myPos[1]), (myPos[0], myPos[1] + 1), (myPos[0], myPos[1] - 1)],
                    [(myPos[0], myPos[1] - 1), (myPos[0], myPos[1] + 1), (myPos[0] + 1, myPos[1])]]
    for comb in combinations:
        surr = True
        for pos in comb:
            surr = surr and gameState.hasWall(int(pos[0]), int(pos[1]))
        if surr:
            return True
    return False

def foodCount(foodGrid):
    res = 0
    for bool in foodGrid.asList():
        if bool:
            res += 1
    return res