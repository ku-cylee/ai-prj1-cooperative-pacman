# myAgents.py
# ---------------
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

from game import Agent, Directions
from searchProblems import PositionSearchProblem

import util
import time
import search

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
def createAgents(num_pacmen, agent='ExclusiveAgent'):
    return [eval(agent)(index=i) for i in range(num_pacmen)]

class SharedGameData:
    def __init__(self):
        self.nextIdx = 1
        self.remainingFoodsCount = None
        self.pretargetedFoods = []

    def resetForNewGame(self, newIdx):
        if self.nextIdx == newIdx:
            self.nextIdx = newIdx + 1
        else:
            self.__init__()

    def addFood(self, foodPosition):
        if foodPosition:
            self.pretargetedFoods.append(foodPosition)
            self.remainingFoodsCount -= 1

    def removeFood(self, foodPosition):
        if foodPosition:
            self.pretargetedFoods.remove(foodPosition)

    def getFoods(self):
        return self.pretargetedFoods

    def setFoodCount(self, state):
        if self.remainingFoodsCount != None:
            return
        self.remainingFoodsCount = sum(row.count(True) for row in state.getFood())

    def isFoodExist(self):
        return self.remainingFoodsCount > 0

shared = SharedGameData()

class ExclusiveAgent(Agent):
    """
    Implementation of your agent.
    """

    def getAction(self, state):
        """
        Returns the next action the agent will take
        """

        "*** YOUR CODE HERE ***"
        if self.path:
            return self.path.pop(0)

        self.shared.removeFood(self.goal)
        self.shared.setFoodCount(state)

        problem = ExclusionSearchProblem(state, self.index, self.shared.getFoods())
        self.goal, self.path = self.getGoalAndPath(problem)

        self.shared.addFood(self.goal)

        return self.path.pop(0)

    def getGoalAndPath(self, problem):
        if not self.shared.isFoodExist():
            return None, [Directions.STOP] * 100
        else:
            return self.breadthFirstSearch(problem)

    def breadthFirstSearch(self, problem):
        return self.treeSearch(problem, util.Queue())

    def treeSearch(self, problem, paths):
        paths.push([(problem.getStartState(), Directions.STOP, 0)])
        visited_states = []

        while not paths.isEmpty():
            currentPath = paths.pop()
            currentState = currentPath[-1][0]

            if problem.isGoalState(currentState):
                return currentState, [path[1] for path in currentPath[1:]]

            if currentState in visited_states:
                continue

            visited_states.append(currentState)

            for successor_node in problem.getSuccessors(currentState):
                if successor_node[0] not in visited_states:
                    paths.push(currentPath + [successor_node])

        return None, Directions.STOP

    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        "*** YOUR CODE HERE"
        self.path = []
        self.goal = None
        self.shared = shared
        self.shared.resetForNewGame(self.index)

class ExclusionSearchProblem(PositionSearchProblem):

    def __init__(self, gameState, agentIdx, excludedNodes):
        self.food = gameState.getFood()

        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIdx)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0

        self.excludedNodes = excludedNodes

    def isGoalState(self, state):
        x, y = state
        return (state not in self.excludedNodes) and self.food[x][y]

"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""

class ClosestDotAgent(Agent):

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition(self.index)
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState, self.index)


        "*** YOUR CODE HERE ***"

        pacmanCurrent = [problem.getStartState(), [], 0]
        visitedPosition = set()
        # visitedPosition.add(problem.getStartState())
        fringe = util.PriorityQueue()
        fringe.push(pacmanCurrent, pacmanCurrent[2])
        while not fringe.isEmpty():
            pacmanCurrent = fringe.pop()
            if pacmanCurrent[0] in visitedPosition:
                continue
            else:
                visitedPosition.add(pacmanCurrent[0])
            if problem.isGoalState(pacmanCurrent[0]):
                return pacmanCurrent[1]
            else:
                pacmanSuccessors = problem.getSuccessors(pacmanCurrent[0])
            Successor = []
            for item in pacmanSuccessors:  # item: [(x,y), 'direction', cost]
                if item[0] not in visitedPosition:
                    pacmanRoute = pacmanCurrent[1].copy()
                    pacmanRoute.append(item[1])
                    sumCost = pacmanCurrent[2]
                    Successor.append([item[0], pacmanRoute, sumCost + item[2]])
            for item in Successor:
                fringe.push(item, item[2])
        return pacmanCurrent[1]

    def getAction(self, state):
        return self.findPathToClosestDot(state)[0]

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x,y = state
        if self.food[x][y] == True:
            return True
        return False
