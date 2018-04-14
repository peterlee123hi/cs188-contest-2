# myTeam.py
# ---------------
# used starter code from original baseline.py
# http://ai.berkeley.edu.
"""
Students' Names: Laura Smith, Arsh Zahed
Contest Number: 2
Description of Bot: We used the same template as the baseline team, but we changed the features and rewards.
For the offensive agent, we noticed that the greedier the agent, the more likely it would die. 
So, in order to guarantee at least some points were gained, we introduced an instance variable corresponding 
to the latent pellets eaten and incorporated that into the reward (encouraged the agent to avoid death and return
to its home side as quickly as possible). This instance variable is controlled by the actual action-taking.
"""
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
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
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
class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  eaten = 0
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    foodLeft = len(self.getFood(gameState).asList())
    if len(self.getFood(self.getSuccessor(gameState, bestActions[0])).asList()) < foodLeft:
      self.eaten += 1
    myPos = gameState.getAgentState(self.index).getPosition()
    if gameState.data.layout.width/2.0 - 1 == myPos[0]:
      self.eaten = 0 
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
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)
    # Compute distance to the nearest food
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    oldEnemies = [gameState.getAgentState(i).getPosition() for i in self.getOpponents(gameState)]
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    eaters = [a for a in enemies if (not a.isPacman) and a.getPosition() != None]
    if len(eaters) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in eaters]
      features['minEaterDistance'] = min(dists)**(.6)
      if min(dists) <= 2:
        features['minEaterDistance'] = -1000
    if myPos == oldEnemies[0] or myPos == oldEnemies[1]:
      features['minEaterDistance'] = -100000
    if self.eaten > 0:
      features['onDefense'] = 1
      features['dist2center'] = abs(successor.data.layout.width/2.0 - myPos[0])
      if myPos[0] < successor.data.layout.width/2.0:
        features['dist2center'] = -100000
    else:
      features['dist2center'] = 1
    if (len(eaters) == 0):
      features['dist2center'] = 0
    temp = gameState.getBlueCapsules()
    dTC = 0
    if temp:
      minc = min(temp)
      if (features['minEaterDistance']<=6 and minc <= 9):
        dTC = self.getMazeDistance(myPos, temp[0])
    features['distToCap'] = dTC**(.5)
    return features
  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'minEaterDistance':1.5, 'dist2center': -100, 'distToCap':-1.2}
class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """
  eaten = 0
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    foodLeft = len(self.getFood(gameState).asList())
    if len(self.getFood(self.getSuccessor(gameState, bestActions[0])).asList()) < foodLeft:
      self.eaten += 1
    myPos = gameState.getAgentState(self.index).getPosition()
    if gameState.data.layout.width/2.0 - 1 == myPos[0]:
      self.eaten = 0 
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
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    oldOpponents = [gameState.getAgentState(i) for i in self .getOpponents(gameState)]
    oldInvaders = [a.getPosition() for a in oldOpponents if a.isPacman and a.getPosition() != None]
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    #Offense
    if len(oldInvaders) == 0 and len(invaders) == 0:
      foodList = self.getFood(successor).asList()  
      features['successorScore'] = -len(foodList)#self.getScore(successor)
      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance
        oldEnemies = [gameState.getAgentState(i).getPosition() for i in self.getOpponents(gameState)]
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        eaters = [a for a in enemies if (not a.isPacman) and a.getPosition() != None]
        if len(eaters) > 0:
          dists = [self.getMazeDistance(myPos, a.getPosition()) for a in eaters]
          features['minEaterDistance'] = min(dists)**(.65)
          if min(dists) <= 2:
            features['minEaterDistance'] = -1000
        if myPos == oldEnemies[0] or myPos == oldEnemies[1]:
          features['minEaterDistance'] = -100000
        if self.eaten > 0:
          features['onDefense'] = 1
          features['dist2center'] = abs(successor.data.layout.width/2.0 - myPos[0])
          if myPos[0] < successor.data.layout.width/2.0:
            features['dist2center'] = -1000000
        else:
          features['dist2center'] = 1
        temp = gameState.getBlueCapsules()
        dTC = 0
        if temp:
          minc = min(temp)
          if (features['minEaterDistance']<=6 and minc <= 9):
            dTC = self.getMazeDistance(myPos, temp[0])
        features['distToCap'] = dTC**(.5)
    #Defense
    else:
    # Computes whether we're on defense (1) or offense (0)
      features['onDefense'] = 1
      if myState.isPacman: features['onDefense'] = 0
      # Computes distance to invaders we can see
      features['numInvaders'] = len(invaders)
      if len(invaders) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        features['invaderDistance'] = min(dists)
      if action == Directions.STOP: features['stop'] = 1
      rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
      if action == rev: features['reverse'] = 1
      features['dist2center'] = abs(successor.data.layout.width/2 - myPos[0])
      if features['numInvaders'] >= 1:
        features['dist2center'] = 0
      for p in oldInvaders:
        if myPos[0] == p[0] and myPos[1] == p[1]:
          features['invaderDistance'] = 0
    return features
  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100,'dist2center': -5, 'invaderDistance': -10, 'stop': -100, 'reverse': -2,
              'successorScore': 100, 'distanceToFood': -1, 'minEaterDistance':1.5, 'distToCap':-1.2}
