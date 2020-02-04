from copy import deepcopy

import agent
import environment
from agent import Agent, AgentState
from helper_funcs import print_debug, print_info


class SearchNode:
    T = 0

    def __init__(self, parent, depth, action, path_cost, state, initial_state):
        """
        :type parent: SearchNode
        :type depth: int
        :type path_cost: int
        :type state: agent.AgentState
        """
        self.parent_node = parent
        self.action = action
        self.initial_state = deepcopy(initial_state)
        self.state = state
        self.path_cost = path_cost
        self.depth = depth

        self.expansions = 0

    @staticmethod
    def solution(node):
        action_seq = []
        curr_node = node
        while curr_node.parent_node:
            action_seq.insert(0, curr_node.action)
            curr_node = curr_node.parent_node
        return action_seq

    def realtime_solution(self, node):
        action_seq = []
        curr_node = node
        while curr_node != self:
            action_seq.insert(0, curr_node.action)
            curr_node = curr_node.parent_node
        return action_seq

    def greedy_search(self, problem):
        frontier = GreedySearchNodePriorityQueue(self)
        explored_states = []
        while True:
            if frontier.is_empty():
                print_info("FRONTIER EMPTY, USED " + str(self.expansions) + " EXPANSIONS")
                res = self.solution(node)
                res.append("TERMINATE")
                return res
            node = frontier.pop()
            frontier.delete_all()
            if goal_test(problem, node.state):
                print_info("CALCULATED ALL ACTIONS, TOOK " + str(self.expansions) + " EXPANSIONS, ACTION COUNT: " +
                           str(node.depth))
                return self.solution(node)
            explored_states.append(self.state)
            time_calculating = int(self.expansions * self.T)
            if time_calculating >= 1:
                node.state.time += time_calculating
            child_nodes = expand(node, problem)
            print_debug("CURRENT EXPANSIONS: " + str(self.expansions) + " FRONTIER LENGTH: " + str(len(frontier.queue)))
            if child_nodes:
                for child in child_nodes:
                    explored = False
                    in_frontier = False
                    for state in explored_states:
                        if repeat_state_check(child.state, state):
                            explored = True
                    for n in frontier.queue:
                        if child.state == n.state:
                            in_frontier = True
                            frontier_duplicate = n
                    if not explored and not in_frontier:
                        frontier.insert(child)
                    elif in_frontier:
                        frontier.replace(frontier_duplicate, child)

    def a_star_search(self, problem, limit):
        frontier = AStarSearchNodePriorityQueue(self)
        time_calculating = int(limit * self.T)
        if time_calculating >= 1:
            self.state.time += time_calculating
        explored_states = []
        while True:
            if frontier.is_empty():
                print_debug("FRONTIER EMPTY, USED " + str(self.expansions) + " EXPANSIONS")
                res = self.solution(node)
                res.append("TERMINATE")
                return res
            node = frontier.pop()
            if goal_test(problem, node.state):
                print_info("CALCULATED ALL ACTIONS, TOOK " + str(self.expansions) + " EXPANSIONS")
                print_info("PATH COST: " + str(node.path_cost))
                return self.solution(node)
            explored_states.append(self.state)
            print_debug("CURRENT EXPANSIONS: " + str(self.expansions) + " FRONTIER LENGTH: " + str(len(frontier.queue)))
            if self.expansions > limit:
                print_info("REACHED LIMIT OF EXPANSIONS!! FAIL!!")
                res = self.solution(node)
                res.append("TERMINATE")
                return res
            child_nodes = expand(node, problem)
            if child_nodes:
                for child in child_nodes:
                    explored = False
                    in_frontier = False
                    for state in explored_states:
                        if repeat_state_check(child.state, state):
                            explored = True
                    for n in frontier.queue:
                        if child.state == n.state:
                            in_frontier = True
                            frontier_duplicate = n
                    if not explored and not in_frontier:
                        frontier.insert(child)
                    elif in_frontier:
                        frontier.replace(frontier_duplicate, child)

    def __eq__(self, other):
        """
        :type other: SearchNode
        """
        return self.parent_node == other.parent_node and \
               self.action == other.action and \
               self.initial_state == other.initial_state and \
               self.state == other.state and \
               self.path_cost == other.path_cost and \
               self.depth == other.depth


class NodePriorityQueue:
    def __init__(self, node=None):
        self.queue = []  # type: list[SearchNode]
        if node:
            self.insert(node)

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    # for checking if the queue is empty
    def is_empty(self):
        return len(self.queue) == 0

    # for inserting an element in the queue
    def insert(self, node):
        self.queue.append(node)

    # for popping an element based on Priority
    def pop(self):
        return None

    def replace(self, old_n, new_n):
        self.queue.remove(old_n)
        self.insert(new_n)

    def delete_all(self):
        self.queue = []


class GreedySearchNodePriorityQueue(NodePriorityQueue):
    def __init__(self, node=None):
        NodePriorityQueue.__init__(self, node)

    def pop(self):
        try:
            # f = h
            best_node_index = 0
            best_node_h = heuristic(self.queue[0])
            for i in range(len(self.queue)):
                curr_h = heuristic(self.queue[i])
                if curr_h <= best_node_h:
                    if curr_h == best_node_h:
                        if self.queue[i].state.curr_location.index < \
                                self.queue[best_node_index].state.curr_location.index:
                            best_node_index = i
                    else:
                        best_node_index = i
                        best_node_h = curr_h
            best_node = self.queue[best_node_index]
            del self.queue[best_node_index]
            print_debug("POPPING: " + str(best_node.state) + ", g=" + str(best_node.path_cost) + " h=" + \
                        str(best_node_h))
            return best_node
        except IndexError:
            print()
            exit()


class AStarSearchNodePriorityQueue(NodePriorityQueue):
    def __init__(self, node=None):
        NodePriorityQueue.__init__(self, node)

    def pop(self):
        try:
            # f = h + g
            best_node_index = 0
            best_node_f = heuristic(self.queue[0]) + self.queue[0].path_cost
            for i in range(len(self.queue)):
                curr_f = heuristic(self.queue[i]) + self.queue[i].path_cost
                if curr_f <= best_node_f:
                    if curr_f == best_node_f:
                        if self.queue[i].state.curr_location.index < \
                                self.queue[best_node_index].state.curr_location.index:
                            best_node_index = i
                    else:
                        best_node_index = i
                        best_node_f = curr_f
            best_node = self.queue[best_node_index]
            del self.queue[best_node_index]
            print_debug("POPPING: " + str(best_node.state) + ", g=" + str(best_node.path_cost) + " h=" + \
                        str(best_node_f - best_node.path_cost))
            return best_node
        except IndexError:
            print()
            exit()


def successor_fn(problem, curr_state):
    """
    :type curr_state: agent.AgentState
    """
    res_state = deepcopy(curr_state)
    # Check for hurricane or  termination
    if curr_state.state_hurricane_check() or curr_state.is_terminated:
        return None, res_state

    actions = []  # type: list[str]
    res_states = []  # type:list[AgentState]
    # Removing blocked edges
    edges = [edge for edge in curr_state.curr_location.connected_edges if not edge.is_blocked]
    for edge in edges:
        actions.append(str(edge))
        # Building the dest state
        dest_state = deepcopy(res_state)
        # Updating dest and time
        dest_state.state_traverse(edge)
        # checking if successfully arrived
        if dest_state.curr_location.deadline >= dest_state.time and \
                curr_state.time + edge.weight - 1 <= curr_state.curr_location.deadline:
            # Picking up or loading off people
            dest_state.state_pickup_loadoff_update()
        # Dead
        else:
            dest_state.is_terminated = True
        # Updating people at location according to deadlines past
        dest_state.state_v_people_update()
        res_states.append(dest_state)

    # The option of a terminate action
    actions.append("TERMINATE")
    res_state.state_terminate()
    res_state.time_update()
    res_state.state_v_people_update()
    res_states.append(res_state)

    return [(actions[i], res_states[i]) for i in range(len(actions))]


def step_cost(node1, action, res_state):
    """
    :type node1: SearchNode
    :type action: str
    :type res_state: AgentState
    """
    dead_ppl = 0
    # Getting deadlines at all vertices of the graph
    arr = [(v.index, v.deadline) for v in node1.state.curr_location.graph.vertices]
    for (index, deadline) in arr:
        # People in the new state died in this vertice
        if deadline < res_state.time:
            dead_ppl += node1.state.v_people[index - 1]
    # Terminated in non shelter or died by hurricane
    if (not res_state.curr_location.is_shelter() and res_state.is_terminated) or \
            (res_state.is_terminated and action != "TERMINATE"):
        # Counting the amount of people dying from this termination: carrying, people in the rest of the locations, and
        # people that died from deadlines anyway
        return res_state.p_carrying + sum(res_state.v_people) + dead_ppl + res_state.k_value
    else:
        return dead_ppl


def heuristic(node):
    """
    :type node: SearchNode
    """

    if goal_test(None, node.state):
        return 0
    # If will terminate in this node, amount of people we won't be able to save
    if node.state.is_terminated:
        return sum(node.state.v_people) + node.state.p_carrying
    # MY ADDITION: if arrived in "last minute" to location, need to see if we can even leave it.
    if node.state.curr_location.deadline == node.state.time:
        if min([e.weight for e in node.state.curr_location.connected_edges]) > 1 and \
                not node.state.curr_location.is_shelter():
            return sum(node.state.v_people) + node.state.p_carrying  # Dead

    curr_vertex = node.state.curr_location
    n_v = len(node.state.v_people)

    # Getting shortest distances
    g_vertices, dist, paths = dijkstra_without_graph(curr_vertex, n_v)

    can_reach_shelter = False
    # If we're carrying people, we need to check if this state can reach a shelter
    if node.state.p_carrying > 0:
        for i in range(len(g_vertices)):
            # If this is a shelter we can reach
            if g_vertices[i].is_shelter() and dist[i] <= (g_vertices[i].deadline - node.state.time):
                can_reach_shelter = True
        if not can_reach_shelter:
            return node.state.p_carrying + sum(node.state.v_people)

    # Our standard heuristic:  people we know we can reach and save
    res = 0
    for i in range(len(g_vertices)):
        if g_vertices[i].deadline >= node.state.time and dist[i] > (g_vertices[i].deadline - node.state.time):
            res += node.state.v_people[i]

    return res


def expand(node, problem):
    """
    :type node: SearchNode
    :type problem: environment.Environment
    """
    successors = []  # type: list[SearchNode]
    successor_fn_output = successor_fn(problem, node.state)
    node.expansions = 1
    tmp_node = node.parent_node
    while tmp_node:
        tmp_node.expansions += 1
        tmp_node = tmp_node.parent_node
    if not successor_fn_output[0]:
        return None
    for (action, result_state) in successor_fn_output:
        tot_cost = node.path_cost + step_cost(node, action, result_state)
        s = SearchNode(node, node.depth + 1, action, tot_cost, result_state, node.initial_state)
        successors.append(s)
    return successors


def goal_test(problem, state):
    """

    :type state: AgentState
    """
    no_more_people = [0] * len(state.v_people) == state.v_people
    not_carrying = 0 == state.p_carrying
    is_terminated = state.is_terminated == True
    in_a_shelter = state.curr_location.is_shelter()
    # Optional
    saved_all = True
    # saved_all = state.ppl2save == state.p_saved
    return no_more_people and not_carrying and is_terminated and in_a_shelter and saved_all


def repeat_state_check(been_state, dest_state):
    """

    :type been_state: AgentState
    :type dest_state: AgentState
    """
    return been_state.curr_location == dest_state.curr_location and \
        been_state.p_carrying == dest_state.p_carrying and \
        been_state.p_saved == dest_state.p_saved and \
        been_state.is_terminated == dest_state.is_terminated

    # return False


class GreedySearchAgent(Agent):
    def __init__(self, index, initial_state):
        """

        :type initial_state: agent.AgentState
        :type index: int
        """
        Agent.__init__(self, index, initial_state)
        self.been_there = [deepcopy(initial_state)]
        self.curr_node = SearchNode(None, 0, None, 0, initial_state, initial_state)

    def action_old(self, percept):
        ag_env = percept
        if len(self.seq) > 0:
            action = self.seq.pop(0)
            return action
        self.curr_state.v_people = ag_env.get_people_array_considering_deadlines()
        print_debug("GREEDY SEARCH AGENT " + str(self) + " ACTION:")
        print_debug("CHECKING IF CURRENT IS GOAL:")
        if goal_test(ag_env, self.curr_state):
            return "TERMINATE"
        print_debug("EXPANDING:")
        successors = expand(self.curr_node, ag_env)
        for i in range(len(successors)):
            print_debug(str(i) + ". ACTION: " + str(successors[i].action) + ", STATE: " + str(successors[i].state))

        print_debug("CHECKING FOR GOALS:")
        for s in successors:
            # print_debug(str(s.state))
            # print_debug(str(s.state.v_people))
            if goal_test(ag_env, s.state):
                print_debug("FOUND GOAL: " + str(s.state))
                return s.action

        #  Removing repeat states
        tmp_successors = successors[:]
        for s in tmp_successors:
            for state in self.been_there:
                if repeat_state_check(s.state, state):
                    successors.remove(s)
                    print_debug("REMOVED REPEATED STATE " + str(s.action) + ", " + str(s.state))

        #  Using heuristics
        best_s = None
        best_h = float("inf")
        for s in successors:
            h = heuristic(s)
            print_debug("H: " + str(s.action) + ", h=" + str(h))
            if h <= best_h:
                best_s = s
                best_h = h
        print_debug("CHOSE " + str(best_s.action) + " BECAUSE OF h=" + str(best_h))
        print_debug("PATH COST IS: " + str(best_s.path_cost))
        self.been_there.append(deepcopy(best_s.state))
        self.curr_node = best_s
        return best_s.action

    def action(self, percept):
        ag_env = percept
        if not self.seq:
            self.seq = self.curr_node.greedy_search(None)
        next_action = self.seq.pop(0)
        return next_action


class AStarSearchAgent(Agent):
    LIMIT_DEFAULT_VALUE = 100000

    def __init__(self, index, initial_state, limit=LIMIT_DEFAULT_VALUE):
        """

        :type initial_state: agent.AgentState
        :type index: int
        """
        Agent.__init__(self, index, initial_state)
        self.curr_node = SearchNode(None, 0, None, 0, initial_state, initial_state)
        self.limit = limit

    def action(self, percept):
        ag_env = percept
        if not self.seq:
            self.seq = self.curr_node.a_star_search(None, self.limit)
        next_action = self.seq.pop(0)
        return next_action
