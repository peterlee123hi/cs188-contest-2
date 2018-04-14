"""
Students' Names: Sonthaya Visuthikraisee and Joan Zhu
Contest Number: 2
Description of Bot: our bot chooses between a defensive and an offensive strategy depending on location of enemies, self, food, etc.
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
import random, time, util
from game import Directions
import game
from util import nearestPoint


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

  """
  Things to consider:
  -location of food pellets we want to eat AND also of those we want to defend
  -what team we're on
  -what side of the board we're on 
  -location of our opponents
  -location of capsules (to make enemies scared)
  -location of our own capsules (that will make us scared)
  -if the opponents are scared
  -if we are scared dont approach invaders
  -don't care how close invaders are to food, only how close they are to getting back to their side
  -if we have eaten more than 5 capsules always return to side
  """

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
    self.start = gameState.getAgentPosition(self.index)


  def chooseAction(self, gameState):

    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

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


    #THIS IS THE METHOD WE WANNA CHANGE
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    us = [successor.getAgentState(i) for i in self.getTeam(successor)]
    us.remove(myState)

    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    non_invader_enemies = [a for a in enemies if not a.isPacman and a.getPosition() != None]


    defense_prob = 1.0 * len(invaders)/len(enemies)

    closest_food_distance = float("+inf")

    food_we_are_defending = self.getFoodYouAreDefending(gameState)

    #print(successor.getAgentState(self.index).scaredTimer)
    #print(successor.getAgentState(self.index).numCarrying)
    #print(successor.getAgentState(self.index).numReturned)


    for invader in invaders:
      for rows in range(food_we_are_defending.height):
        for cols in range(food_we_are_defending.width):
          if food_we_are_defending[cols][rows]:
            distance_invasion = self.getMazeDistance(invader.getPosition(), (cols, rows))
            if (distance_invasion < closest_food_distance):
              defense_prob += 1/(distance_invasion + 1)
              closest_food_distance = distance_invasion

      defense_prob += 1/self.getMazeDistance(myState.getPosition(), invader.getPosition())
      defense_prob += 1/(food_we_are_defending.width - invader.getPosition()[0] + 1)

    for non_invader in non_invader_enemies:
      defense_prob -= 1/self.getMazeDistance(myState.getPosition(), non_invader.getPosition())

    # if (food_we_are_defending.width - us[0].getPosition()[0]) > 0:
    #   defense_prob -= 0.1

    if (successor.getAgentState(self.index).numCarrying > 3):
      defense_prob = 1

    if (defense_prob >= 0.5):
      print("defensive")
      features = self.getDefensiveFeatures(gameState, action)
      weights = self.getDefensiveWeights(gameState, action)
      self.model = 0
    else:
      print("offensive")
      features = self.getOffensiveFeatures(gameState, action)
      weights = self.getOffensiveWeights(gameState, action)
      self.model = 1
    

    return features * weights

  def getDefensiveFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    us = [successor.getAgentState(i) for i in self.getTeam(successor)]
    us.remove(myState)
    partnerPos = us[0].getPosition()

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

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getDefensiveWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10000, 'stop': -100, 'reverse': -2}


  def getOffensiveFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    us = [successor.getAgentState(i) for i in self.getTeam(successor)]
    us.remove(myState)
    partnerPos = us[0].getPosition()

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    non_invader_enemies = [a for a in enemies if not a.isPacman and a.getPosition() != None]

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    # Compute distance to enemy capsule

    if self.red:myCapsules = gameState.getBlueCapsules()
    else: myCapsules = gameState.getRedCapsules()

    if len(myCapsules) > 0: 
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in myCapsules])
      features['distanceToFood'] = minDistance

    features['distanceFromPartner'] = self.getMazeDistance(myPos, partnerPos)
    features['distanceToNonInvaders'] = min([self.getMazeDistance(myPos, enemy.getPosition()) for enemy in non_invader_enemies])

    return features



  def getOffensiveWeights(self, gameState, action):
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    us = [successor.getAgentState(i) for i in self.getTeam(successor)]
    us.remove(myState)
    food_we_are_defending = self.getFoodYouAreDefending(gameState)

    if (food_we_are_defending.width - us[0].getPosition()[0]) > 0:
      weight = 0
    else:
      weight = 5
    return {'successorScore': 100, 'distanceToFood': -1, 'distanceToCapsule': 50, 'distanceFromPartner': weight, 'distanceToNonInvaders': weight * 25}







