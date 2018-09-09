from itertools import chain
from builtins import map
import math
import random
import cv2
import src.vistools as vis
import src.utils as utils
from .environment import Prism
import math

class Node(object):

    def __init__(self, start, goal, cost):
        self.distance = math.hypot(goal[0] - start[0], goal[1] - start[1])
        self.cost = cost
        self.totalCost = self.distance + cost
        self.start = start  # Node position
        self.goal = goal    # Goal position
        self.id = id(self)  # Unique identifier for class instance
        self.children = []
        self.parent = None
        self.done = False   # Only true for goal node

    def __iter__(self):
        for v in chain(*map(iter, self.children)):
            yield v
        yield self

    def add_child(self, obj):
        self.children.append(obj)


def expand_tree(node):

    pathReversed = []
    pathReversed.append(node.start)
    while node.parent is not None:
        pathReversed.append(node.parent.start)
        node = node.parent

    return pathReversed


def generate_node(parent, sample, stepSize):

    deltaX = sample[0] - parent.start[0]
    deltaY = sample[1] - parent.start[1]

    if abs(deltaX) > abs(deltaY):   # Generate new sample on X or Y axis of parent node. Randomise new edge length.
        newX = parent.start[0] + stepSize * utils.sign(deltaX) * random.random()
        update = Node((newX, parent.start[1]), parent.goal, parent.cost + newX - parent.start[0])
    else:
        newY = parent.start[1] + stepSize * utils.sign(deltaY) * random.random()
        update = Node((parent.start[0], newY), parent.goal, parent.cost + newY - parent.start[0])

    update.parent = parent
    return update


def generate_path(env, startNode, endNode, stepSize, boxClearance, plot=False):

    # Store euclidean distance heuristic in root node
    newTree = Node(startNode, endNode, 0)
    env.add_tree(newTree)

    while True:
        # Generate valid sample while candidate point not in collision with world
        samplePoint = env.sample()

        if plot:
            canvas = vis.plot_sample(env.show((1000, 1000, 3), treeID=id(newTree)), samplePoint, (1000, 1000, 3))
            cv2.imshow(
                'environment', canvas)
            cv2.waitKey(1)

        # Select closest node to sample point by iterating through nodes
        closestNode = 1
        for node in iter(newTree):
            sampleDistance = math.hypot(samplePoint[0] - node.start[0], samplePoint[1] - node.start[1])
            if sampleDistance <= closestNode:
                closestNode = sampleDistance

        # And then update node with sample point at position
        for node in iter(newTree):
            sampleDistance = math.hypot(samplePoint[0] - node.start[0], samplePoint[1] - node.start[1])
            if sampleDistance == closestNode: # add child

                newNode = generate_node(node, samplePoint, stepSize)

                if not env.collides_with_box(
                        Prism(env.boxes[0].width * boxClearance, env.boxes[0].height * boxClearance, newNode.start)):
                    node.add_child(newNode)

            # Check for win condition
            if node.distance <= stepSize:
                path = expand_tree(node)

                # Plot path in red
                if plot:
                    for point in range(1, len(path)):
                        cv2.imshow('environment',
                                   cv2.line(canvas,
                                            (int(path[point - 1][0] * 1000), int(path[point - 1][1] * 1000)),
                                            (int(path[point][0] * 1000), int(path[point][1] * 1000)), [0, 0, 255], 2))
                    cv2.waitKey(0)

                return path
