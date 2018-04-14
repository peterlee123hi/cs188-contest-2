"""
Students' Names: Swapnil Das, Edward Sa
Contest Number: 2
Description of Bot: Our bot mainly focuses on offense, to pressure teams that rely on a more standard baseline offense/defense approach.
The way it works is as follows:
1. Pressure the opposing team with two attacking Pacmen collecting as many dots as possible. Their evaluation functions
are such that they will retreat to deposit points they've earned and avoiding getting too greedy, and that their retreat
is a function proportional to the number of points they have in storage to deposit.
2. The bots return back to their base to hound down attackers that try eat their pellets once the percentage of pellets 
consumed is above a certain fraction. After killing off any opposing pacmen, they will patrol the cloud of food pellets 
left in the wake of defeating the Pacment to prevent further attempts at attacking it.
3. There is further emergency protocol in the case of having returned but without a lead, in which case one of the defenders
now goes and attacks to make up for the points. While this has yet to be tested in practice because of the way dummy_bot.py 
and baselineTeam.py play out, we believe it can make a difference in the worst case situation.
We use alpha-beta pruning and a depth 1 minimax tree (we would use depth 2, but it tends to go over 1 second more than thrice
on average on our system, so it's best not to lose by forfeit.)
"""
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
# helper function:
def flip(num):
  return -1 * num
def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffenseAgent', second = 'OffenseAgent'):
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
class OffenseAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.start = gameState.getAgentPosition(self.index)
    self.oppStart = [gameState.getAgentPosition(i) for i in self.getOpponents(gameState)][0]
    self.registerTeam(self.getTeam(gameState))
    self.buddyIndex = [i for i in self.agentsOnTeam if i != self.index][0]
    self.accumulated = 0
    self.maxFood = len(self.getFood(gameState).asList())
    self.warningWatch = 0
    self.emergency = False
    self.depth = 1
    self.differential = False
  def chooseAction(self, gameState):
    start = time.time()
    actions = gameState.getLegalActions(self.index)
    bestActionCurr = self.getActionRecursive(gameState, self.index, 0)
    foodLeft = len(self.getFood(gameState).asList())
    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.distancer.getDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      bestActionCurr = bestAction
    successorCurr = self.getSuccessor(gameState, bestActionCurr)
    foodTaken = self.getFood(successorCurr).asList()
    willBePacman = successorCurr.getAgentState(self.index).isPacman
    if len(foodTaken) < foodLeft:
      self.accumulated += 1
    if not willBePacman:    
      self.accumulated = 0 
    timeTaken = time.time() - start
    if timeTaken > 1:
      self.warningWatch += 1
    if self.warningWatch == 3:
      return None
    return bestActionCurr
  def maximizer(self, gameState, currDepth, agentIndex, alpha, beta):
    actions = gameState.getLegalActions(agentIndex)
    currDepth -= 1 
    if currDepth < 0: # finished game or hit bottom, need to get value
      return (self.evaluate(gameState), None)
    value = float("-inf") 
    actions.remove(Directions.STOP)  
    for action in actions:      
      successorState = gameState.generateSuccessor(agentIndex, action)
      successor = self.minimizer(successorState, currDepth, (agentIndex + 1) % gameState.getNumAgents(), alpha, beta)[0]   
      if successor > value:
        value = successor
        maxMove = action
      if value > beta:
        return (value, maxMove)
      alpha = max(alpha, value)
    return (value, maxMove)
  def minimizer(self, gameState, currDepth, agentIndex, alpha, beta):
    actions = gameState.getLegalActions(agentIndex) 
    if currDepth < 0:
      return (self.evaluate(gameState), None)
    value = float("inf")
    nextPersonToPlay = (agentIndex + 1) % (gameState.getNumAgents())
    if nextPersonToPlay == self.buddyIndex:
      nextPersonToPlay = (nextPersonToPlay + 1) % (gameState.getNumAgents())
    if nextPersonToPlay == self.index:
      evaluater, agentNext = (self.maximizer, self.index)
    else:
      evaluater, agentNext = (self.minimizer, nextPersonToPlay)
    for action in actions:      
      successorState = gameState.generateSuccessor(agentIndex, action)
      successor = evaluater(successorState, currDepth, agentNext, alpha, beta)[0]
      if successor < value:
        value = successor
        minMove = action
      if value < alpha:
        return (value, minMove)
      beta = min(beta, value)          
    return (value, minMove)
  def getActionRecursive(self, gameState, agent, currDepth):
    toReturn = self.maximizer(gameState, self.depth, self.index, float("-inf"), float("inf"))
    return toReturn[1]
  def guarantee(self, array, agent):
    toComp = []
    for elem in array:
      toComp.append(elem[0])
    if agent == self.index or agent == self.buddyIndex:
      index = toComp.index(max(toComp))
    else:
      index = toComp.index(min(toComp))
    return array[index]
  def getSuccessor(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor
  def evaluate(self, gameState):
    features = self.getFeatures(gameState)
    weights = self.getWeights(gameState)
    a = features * weights
    return a
  def getFeatures(self, gameState):
    # setup
    features = util.Counter()
    myself = gameState.getAgentState(self.index)
    partner = gameState.getAgentState(self.buddyIndex)
    myPos = myself.getPosition()
    dist = self.distancer.getDistance
    home = dist(myPos, self.start)
    # successor score to actually get food
    foodList = self.getFood(gameState).asList()
    features['successorScore'] = len(foodList) 
    # distance to the closest food
    if len(foodList) > 0:
      minFood = min([dist(myPos, food) for food in foodList])
      features['distanceToFood'] = minFood 
    # distance to partner
    buddyDist = dist(gameState.getAgentState(self.buddyIndex).getPosition(), myPos)
    features['distanceToBuddy'] = buddyDist
    # guaranteeing some points instead of excess greed
    features['security'] = self.getScore(gameState)
    # enemy analysis
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    threats = [a for a in enemies if a.getPosition() != None]
    eaters = [a for a in enemies if a.isPacman and a.getPosition() != None]
    noneaters = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    fearCount = [enemy.scaredTimer for enemy in enemies]
    capsules = self.getCapsules(gameState)
    distcaps = [dist(myPos, cap) for cap in capsules]
    if not distcaps:
      distcaps = [0]
    # emergency data
    threatDistance = [dist(myPos, a.getPosition()) for a in threats if not a.isPacman]
    allDistance = [dist(myPos, a.getPosition()) for a in threats]
    eaterDistance = [a for a in allDistance if a not in threatDistance]
    if not eaterDistance:
      eaterDistance = [0]
    capDistance = [dist(a.getPosition(), cap) for a in threats for cap in self.getCapsulesYouAreDefending(gameState)]
    capDistanceBetter = [dist(a.getPosition(), cap) for a in eaters for cap in self.getCapsulesYouAreDefending(gameState)]
    defendingNow = [dist(myPos, food) for food in self.getFoodYouAreDefending(gameState).asList()]
    if not threatDistance:
        threatDistance = [100]
    if self.emergency:
      if self.getScore(gameState) < 0 and self.buddyIndex - self.index > 0:
        self.emergency = False
        self.differential = False
      if self.emergency:
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        if defendingNow:
          features['threatDistance'] = flip(min(eaterDistance)) + len(noneaters) * 100 + flip((sum(defendingNow)/len(defendingNow))) * 10
        else:
          features['threatDistance'] = len(noneaters) * 1e9 + flip(min(allDistance))
        features['successorScore'] = 0
        features['distanceToFood'] = 0
        features['capsules'] = 0
        features['empowerment'] = 0
        features['distanceToBuddy'] = 5
        features['distanceToHome'] = 0
        return features
    if not myself.isPacman and not self.getScore(gameState):
      features['distanceToFood'] *= 5
      features['security'] = -100000      
    # if non-zero number of threats in vicinity
    elif len(threats) > 0:
      # threats in general as an offensive unit
      features['threatDistance'] = min(threatDistance)
      # close proximity behavior
      if min(threatDistance) <= 4:
        features['distanceHome'] = flip(home * 100 * self.accumulated)
        features['threatDistance'] *= 2000
        if max(fearCount) == 0:
          features['capsules'] = min(distcaps) * 1e3 + len(distcaps) * 100000
        elif min(fearCount) > 0:
          features['threatDistance'] *= flip(2e6)
        else:
          features['capsules'] = min(distcaps) * 2 + len(distcaps) * 100000
      # free reign
      elif min(threatDistance) >= 15:
        features['distanceHome'] = 0
        features['threatDistance'] = 0
        features['capsules'] = 0
        if self.accumulated >= 2 * self.maxFood // 5:
          features['distanceHome'] = flip(home * 100 * self.accumulated)
      # more standard in-game behavior
      else:
        if max(fearCount) == 0:
          features['capsules'] = min(distcaps) * 100 + len(distcaps) * 1e10
        elif min(fearCount) > 0:
          features['threatDistance'] *= flip(2e6)
        else:
          features['capsules'] = min(distcaps) * 0.4 + len(distcaps) * 1e10
        if self.accumulated >= 8:
          features['distanceHome'] = flip(home * self.accumulated * 10)
    else:
      features['capsules'] = min(distcaps) + len(distcaps) * 100000
      features['distanceHome'] = home
    if self.getScore(gameState) > 0:
      self.differential = True
    # emergency protocol
    if len(self.getFoodYouAreDefending(gameState).asList()) < 9 * self.maxFood // 16 and self.differential:
      self.differential = False
      self.emergency = True
      if eaterDistance:
        features['threatDistance'] = flip(min(eaterDistance) * 1e20)
      else:
        features['threatDistance'] = flip(min(allDistance) * 1e20)
      features['security'] = 0
      features['successorScore'] = 0
      features['distanceToFood'] = 0
      features['capsules'] = 0
      features['empowerment'] = 0
      features['distanceToBuddy'] = 0
      features['distanceToHome'] = 0
    return features
  def getWeights(self, gameState):
    """
    When the feature is a function of distance:
    > negative weights implies we want to be closer to them, for increasing the magnitude decreases the evaluation value.
    > positive weights implies we want to be farther from them, for increasing the magnitude increases evaluation value.
    When the feature is a function of score or scaredTimer:
    > positive weights imply we want them more (a higher score leads to a higher evaluation feature.)
    > negative weights imply we want them less (a lesser score leads to a lower evaluation feature.)
    """
    weights = {'successorScore': -1000, 
    'distanceToFood': -10,
    'distanceToBuddy': 9,
    'distanceHome': 5, 
    'threatDistance': 0.75,
    'capsules': -4,
    'security': 2e9}
    return weights
    """
    two issues: running away from ghosts nearby, and depositing without need for fear
    fundamental cause: running away from ghosts 'correctly'
    """
    """
    Parameters to Consider:
    On my team's side:
      > distance to nearest foe while I'm not scared
      > distance to other side
      > distance of nearest foe to power pellet?
      > amount of scaredTimer left.
      > distance to buddy
    On the opposing team's side:
      > successor score is not that big a factor, but obviously important.
      > distance to nearest food pellet on the opposing side.
      > distance to nearest power capsule on the opposing side.
      > distance to nearest foe on your side.
    """
