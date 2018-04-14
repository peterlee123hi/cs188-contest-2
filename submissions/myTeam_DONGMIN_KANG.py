"""
Students' Names: Dongmin Kang
Contest Number: 2
Description of Bot: There are two kinds of bots. One is attacker and another is defenderself.
Agents tend to get more score, but with a probability p, it doesn't. defender
uses reflex agent using score-maximizing actions considering the position of opponents
and position of nearest food and so on.
"""
# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint
from util import flipCoin
#################
# Team creation #
#################
def createTeam(firstIndex, secondIndex, isRed,
               first = 'attacker', second = 'defender'):
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
class myAgent(CaptureAgent):
  """
  There are two types of agents.
  """
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.start = gameState.getAgentPosition(self.index)
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    p=0.9
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    foodLeft = len(gameState.getRedFood().asList())
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
    if flipCoin(p):
        return random.choice(bestActions)
    else:
        return random.choice(actions)
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
  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features
  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}
class attacker(myAgent):
    """
    A reflex agent that tends to seek food.
    """
    def getFeatures(self, gameState, action):
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      foodList = self.getFood(successor).asList()
      features['successorScore'] = -len(foodList)#self.getScore(successor)
      # Compute distance to the nearest food
      if len(foodList) > 0:
        myPos = successor.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance
      return features
    def getWeights(self, gameState, action):
      return {'successorScore': 100, 'distanceToFood': -1}
class defender(myAgent):
    """
    A reflex agent that tends to prevent opponent to capture foods.
    It predict that oppoents will tends to capture food. Therefore,
    this agent estimate probability that the opponent.
    """
    def getFeatures(self, gameState, action):
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      myState = successor.getAgentState(self.index)
      myPos = myState.getPosition()
      # Computes whether we'er attacking or not
      features['onDefense'] = 1
      if myState.isPacman: features['onDefense'] = 0
      # Computes distance to opponents
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      features['numInvaders'] = len(invaders)
      if len(invaders) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        features['invaderDistance'] = min(dists)
      if action == Directions.STOP: features['stop'] = 1
      rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
      if action == rev: features['reverse'] = 1
      foodList = self.getFood(successor).asList()
      if len(foodList) > 0:
        minDistance=0
        for enemy in enemies:
            if enemy.isPacman and enemy.getPosition() != None:
                myPos = enemy.getPosition()
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance
      else:
        features['distanceToFood'] = 0
      return features
    def getWeights(self, gameState, action):
      return {'numInvaders': -1000, 'distanceToFood': 10, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
