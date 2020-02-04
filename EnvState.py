from copy import deepcopy
from graph import *

# from environment import Environment
from helper_funcs import TrueFalseArrayCombinations


class EnvState:
    def __init__(self, ag_loc, people_at_vertices, edges_blocked_status, carrying_count, saved_count, time, is_terminated):
        """

        :type ag_loc: Vertex

        """
        self.ag_loc = ag_loc
        self.people_at_vertices = people_at_vertices
        self.edges_blocked_status = edges_blocked_status
        self.carrying_count = carrying_count
        self.saved_count = saved_count
        self.time = time
        self.is_terminated = is_terminated

    def successor_fn(self):
        res_state = deepcopy(self)
        # Check for hurricane or  termination
        if self.ag_loc.deadline < self.time or self.is_terminated:
            return None, res_state

        actions = []  # type: list[str]
        res_states = []  # type:list[EnvState]
        # Removing blocked edges
        non_blocked_edges = [edge for edge in self.ag_loc.connected_edges if not edge.is_blocked]
        for edge in non_blocked_edges:
            # Building the dest state
            dest_state = deepcopy(res_state)
            # Updating dest and time
            if self.ag_loc == edge.vertex_1:
                dest_v = edge.vertex_2
            else:
                dest_v = edge.vertex_1
            dest_state.time += edge.weight
            dest_state.ag_loc = dest_v
            # checking if successfully arrived
            if dest_v.deadline >= dest_state.time and \
                    self.time + edge.weight - 1 <= self.ag_loc.deadline:
                # Picking up or loading off people
                if dest_v.is_ppl_location():
                    dest_v_ppl_count = self.people_at_vertices[dest_v.index-1]
                    dest_state.carrying_count += dest_v_ppl_count
                    dest_state.people_at_vertices[dest_v.index-1] = 0
                elif dest_v.is_shelter():
                    dest_state.saved_count += self.carrying_count
                    dest_state.people_at_vertices[dest_v.index - 1] += self.carrying_count
                    dest_state.carrying_count = 0
            # Dead
            else:
                dest_state.is_terminated = True
            # Updating people at location according to deadlines past
            for v in dest_state.ag_loc.graph.vertices:
                if v.deadline < dest_state.time:
                    dest_state.people_at_vertices[v.index-1] = 0
            # Updating visible possibly blocked\unblocked edges:
            connected_poss_blocked_edges = []
            for e in dest_state.ag_loc.connected_edges:
                if dest_state.edges_blocked_status[e.index-1] == "U":
                    connected_poss_blocked_edges.append(e)
            if connected_poss_blocked_edges:
                truefalse_perms = TrueFalseArrayCombinations(len(connected_poss_blocked_edges))
                for opt in truefalse_perms:
                    dest_state_opt = deepcopy(dest_state)
                    for i in range(len(connected_poss_blocked_edges)):
                        curr_edge_index = connected_poss_blocked_edges[i].index
                        dest_state_opt.edges_blocked_status[curr_edge_index-1] = opt[i]
                    actions.append(str(edge))
                    res_states.append(dest_state_opt)
            else:
                actions.append(str(edge))
                res_states.append(dest_state)

        # The option of a terminate action
        actions.append("TERMINATE")
        res_state.is_terminated = True
        res_state.time += 1
        for v in res_state.ag_loc.graph.vertices:
            if v.deadline < res_state.time:
                res_state.people_at_vertices[v.index - 1] = 0
        res_states.append(res_state)

        return [(actions[i], res_states[i]) for i in range(len(actions))]

    def getAllPossibleStates(self):
        res = []
        successor_func_output = self.successor_fn()
        if not successor_func_output[0]:
            return []
        for (action, result_state) in successor_func_output:
            res.append(result_state)
            res += result_state.getAllPossibleStates()
        return res

    #  Environment state is of the following structure:
    #  (AgentLocation, PeopleAtVertices?[], EdgesBlocked?[], CarryingCount, Time, SavedCount, Terminated?)
    def __str__(self):
        s = "("
        s += str(self.ag_loc) + ", "
        s += str(self.people_at_vertices) + ", "
        s += str(self.edges_blocked_status) + ", "
        s += str(self.carrying_count) + ", "
        s += str(self.saved_count) + ", "
        s += str(self.time) + ", "
        s += str(self.is_terminated)
        s += ")"

        return s

