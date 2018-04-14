"""
Students' Names: Sharabesh Ramesh, Maggie Donaldson
Contest Number: 2
Description of Bot: Our core bot has two main features: an offensive and defensive end.
The defensive end basically wanders aimlessly until a bot enters its territory
and then follows and kills that bot.
The offensive end tries to capture 3 dots at a time returning to its side after
every iteration. This ensures that it won't get eaten and lose it's progress.
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
import random, time, util
from game import Directions
from util import nearestPoint
import game
#################
# Team creation #
#################
def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefensiveReflexAgent', second = 'OffensiveReflexAgent'):
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
class ReflexCaptureAgent(CaptureAgent):
    """
  A base class for reflex agents that chooses score-maximizing actions
  """
    def registerInitialState(self, gameState):
        # self.distancer.calculateDistance()
        self.start = gameState.getAgentPosition(self.index)
        successor = self.getSuccessor(gameState, Directions.STOP)
        self.foodListCopy = self.getFood(successor).asList()
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
        # TODO: For some reason this is absolute trash and I can't figure out why
        # alphaB_val = self.alphaBetaMinimax(1,gameState,self.index)[1]
        foodLeft = len(self.getFood(gameState).asList())
        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.distancer.getDistance(self.start, pos2)
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction
        return random.choice(bestActions)
        # return alphaB_val
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
    def alphaBetaMinimax(self, depth, gameState, agentnum=0, alpha=-float("INF"), beta=float("INF"), curr=0):
        ####### BASE CASES #############################################
        if depth == 0:
            return (self.evaluate(gameState, Directions.STOP), Directions.STOP)
        # if gameState.isWin() or gameState.isLose():
        #   return self.evaluate(gameState, Directions.STOP)
        ######################## Evaluate Pacman State, the maximizer ########
        if curr == 0:
            nextstates = []
            for act in gameState.getLegalActions(agentnum):
                term = [(
                    self.alphaBetaMinimax(depth, gameState.generateSuccessor(agentnum, act),
                                          (agentnum + 1) % 4, alpha=alpha, beta=beta, curr=(curr + 1) % 4)[
                        0], act)]
                nextstates.extend(term)
                alpha = max(term[0][0], alpha)
                if alpha > beta:
                    break
            return max(nextstates, key=lambda x: x[0])
        ######################## Evaluate Second Pacman State, the maximizer ########
        if curr == 1:
            nextstates = []
            for act in gameState.getLegalActions(agentnum):
                term = [(
                    self.alphaBetaMinimax(depth, gameState.generateSuccessor(agentnum, act),
                                          (agentnum + 1) % 4, alpha=alpha, beta=beta, curr=(curr + 1) % 4)[
                        0], act)]
                nextstates.extend(term)
                alpha = max(term[0][0], alpha)
                if alpha > beta:
                    break
            return max(nextstates, key=lambda x: x[0])
        ################### Evaluate Enemy State, minimizer ###########
        elif curr == 2:
            nextstates = []
            for act in gameState.getLegalActions(agentnum):
                term = [
                    (self.alphaBetaMinimax(depth, gameState.generateSuccessor(agentnum, act),
                                           (agentnum + 1) % 4, alpha=alpha, beta=beta, curr=(curr + 1) % 4)[0], act)]
                nextstates.extend(term)
                beta = min(beta, term[0][0])
                if beta < alpha:
                    break
            return min(nextstates, key=lambda x: x[0])
        ################### Evaluate Enemy State, minimizer ###########
        else:
            nextstates = []
            for act in gameState.getLegalActions(agentnum):
                term = [
                    (self.alphaBetaMinimax(depth - 1, gameState.generateSuccessor(agentnum, act),
                                           (agentnum + 1) % 4, alpha=alpha, beta=beta, curr=(curr + 1) % 4)[0], act)]
                nextstates.extend(term)
                beta = min(beta, term[0][0])
                if beta < alpha:
                    break
            return min(nextstates, key=lambda x: x[0])
class OffensiveReflexAgent(ReflexCaptureAgent):
    """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
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
        # TODO: For some reason this is absolute trash and I can't figure out why
        # alphaB_val = self.alphaBetaMinimax(1,gameState,self.index)[1]
        foodLeft = len(self.getFood(gameState).asList())
        successor = self.getSuccessor(gameState, Directions.STOP)
        myState = successor.getAgentState(self.index)
        if not myState.isPacman:
            self.foodListCopy = list(self.getFood(gameState).asList())
        if abs(foodLeft - len(self.foodListCopy)) > 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.distancer.getDistance(self.start, pos2)
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction
        return bestActions[0]
        # return alphaB_val
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        foodList = self.getFood(successor).asList()
        features['successorScore'] = -len(foodList)  # self.getScore(successor)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        # Compute distance to the nearest food
        if len(foodList) > 0:  # This should always be True,  but better safe than sorry
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.distancer.getDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            home_basers = [a for a in enemies if not a.isPacman and a.getPosition() != None]
            team = [successor.getAgentState(i) for i in self.getTeam(successor)]
            if len(home_basers) > 0: # if things in the enemny territory
              # Get teh smallest distance to a food pellet
                smallest_dist = min([self.distancer.getDistance(myPos, x.getPosition()) for x in home_basers])
                # Only weight distance if you are a pacman
                if myState.isPacman:
                    features['closeToEvil'] = smallest_dist
                    # features['isPacman'] = 1
                else:
                    features['closeToEvil'] = 0
                    # features['isPacman'] = 0
            if myState.isPacman:
                features['isPacman'] = 1
            if action == Directions.STOP:
                features['stopped'] = 1
        return features
    def getWeights(self, gameState, action):
        # I want small numbers for closeToEvil to be bad, and big numbers to be good
        # Small numbers are going to give me a small positive
        # I want to maximize my smallest distance
        return {'successorScore': 100, 'distanceToFood': -10, "closeToEvil": 5, "isPacman": 20, 'stopped': -10000000000}
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
        # Computes whether we're on defense (1) or offense (0)
        features['onDefense'] = 1
        if myState.isPacman: features['onDefense'] = 0
        # Computes distance to invaders we can see
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        # Pacman that are currenly in our territory
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        # One feature is the number of invaders currently attacking us
        features['numInvaders'] = len(invaders)
        # The defense agent only really has stuff to do if people are attacking
        if len(invaders) > 0:
            dists = [self.distancer.getDistance(myPos, a.getPosition()) for a in invaders]
            # Get as close to invader as possible
            features['invaderDistance'] = min(dists)
        #
        if action == Directions.STOP:
            features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        # Prevents us from going back and forth
        if action == rev:
            features['reverse'] = 1
        return features
    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 1000, 'invaderDistance': -10, 'stop': -100000, 'reverse': -2}
