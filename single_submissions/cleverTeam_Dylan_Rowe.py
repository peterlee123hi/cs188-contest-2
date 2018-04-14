# cleverTeam.py
# Student Names: Dylan Rowe, Gao Xian Peh
# Contest Number: 2
#Description of Bot: the basic dummy bot, currently
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint
#################
# Team creation #
#################
def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
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
class DummyAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.start = gameState.getAgentPosition(self.index)
    self.registerTeam(self.getTeam(gameState))
    self.buddyIndex = [i for i in self.agentsOnTeam if i != self.index][0]
  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a) for a in actions]
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
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor
  def evaluate(self, gameState, action):
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)
    myPos = successor.getAgentState(self.index).getPosition()
    if len(foodList) > 0:
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    buddyPos = successor.getAgentState(self.buddyIndex).getPosition()
    budDistance = self.getMazeDistance(myPos, buddyPos)
    features['distanceToBuddy'] = budDistance
    # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    # invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    # features['numInvaders'] = len(invaders)
    # if len(invaders) > 0:
    #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
    #   features['invaderDistance'] = min(dists)
    return features
  def getWeights(self, gameState, action):
    return {'successorScore': 1000, 'distanceToFood': -10, 'distanceToBuddy': 9}
