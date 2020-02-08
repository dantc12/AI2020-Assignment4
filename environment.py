from copy import deepcopy
import random
from agent import ValueIterationAgent, AgentState
from graph import Graph
from helper_funcs import print_debug, print_info, print_query
from EnvState import EnvState
from operator import attrgetter
import timeit


class Environment:

    PERCEPT = None
    K_DEFAULT_VALUE = 2

    VALUE_ITERATION_DELTA = 0.5
    BASE_STATE_REWARD = 0

    def __init__(self, config_file_path, k_value=K_DEFAULT_VALUE):
        self.graph = Graph(config_file_path)
        self.grapCopy = deepcopy(self.graph)
        # self.env_time = 0
        # Array of the actual agents running in the environment
        self.agent = None
        self.agent_score = 0
        self.k_value = k_value  # Penalty related constant

        self.dead_ppl = 0
        self.total_ppl = sum(self.graph.get_people_array_with_shelter())

        s_vertex = self.graph.vertices[0]
        people_at_vertices_count = self.graph.get_people_array()
        edges_blocked_status = self.graph.get_edges_blocked_status()

        self.env_state = EnvState(s_vertex, people_at_vertices_count, edges_blocked_status,
                                  0, 0, 0, False)

        Environment.PERCEPT = self

        self.all_possible_states = []
        self.stateUtilityAndPolicyDict = {}

        print_info("CREATED ENVIRONMENT WITH " + str(self.graph.num_of_vertices()) + " VERTICES, AND " +
                    str(self.graph.num_of_roads()) + " ROADS.")
        print_info("OUR GRAPH:")
        print (str(self.graph))
        print_info("ENVIRONMENT STARTING STATE: " + str(self.env_state))

    def initEnvironmentVariables(self):
        self.agent = None
        self.agent_score = 0
        self.dead_ppl = 0
        self.total_ppl = sum(self.graph.get_people_array_with_shelter())
        s_vertex = self.graph.vertices[0]
        people_at_vertices_count = self.graph.get_people_array()
        edges_blocked_status = self.graph.get_edges_blocked_status()
        self.env_state = EnvState(s_vertex, people_at_vertices_count, edges_blocked_status,
                                  0, 0, 0, False)
        Environment.PERCEPT = self

    def initializeStatesDict(self):
        self.all_possible_states = self.env_state.getAllPossibleStates()
        self.all_possible_states = sorted(self.all_possible_states, key=attrgetter('ag_loc', 'time'))
        print_debug("Number of possible (reachable) states: " + str(len(self.all_possible_states)))
        for s in self.all_possible_states:
            self.stateUtilityAndPolicyDict[str(s)] = (0, "")
        # self.printStatesDict()
        # print_debug("")

    # Determine the edge status for each uncertain edge
    def setRealEdgesStatus(self):
        blockagesInput = input("Enter simulation Blockages (e.g. E21 means edge E2 is blocked):")
        blockagesList = blockagesInput.split()
        for e in self.graph.edges:
            if 0 < e.block_prob < 1:
                res = self.edgeInBlockagesInput(e, blockagesList)
                if res is not -1:
                    e.is_blocked = res
                    continue
                res = random.randint(1, 10)
                if res <= e.block_prob*10:
                    e.is_blocked = True

    def edgeInBlockagesInput(self, edge, blockagesList):
        for b in blockagesList:
            edgeStr = b[0:2]
            val = int(b[2])
            if edge.__eq__(self.graph.get_edge_from_string(edgeStr)):
                if val is 1:
                    return True
                return False
        return -1
    def ValueIteration(self):
        old_dict = deepcopy(self.stateUtilityAndPolicyDict)
        for s in self.all_possible_states:
            state_reward = Environment.BASE_STATE_REWARD
            if s.is_terminated:
                if s.ag_loc.is_shelter() and s.carrying_count == 0:
                    state_reward += s.prev_state.saved_count
                else:
                    state_reward -= self.k_value + s.carrying_count
            max_val = -float("inf")
            best_a = ""
            for a in s.get_pos_actions():
                res_states = s.successor_fn_with_action(a)
                val = 0
                for res_state in res_states:
                    val += old_dict[str(res_state)][0] * s.T(res_state)
                if val > max_val:
                    max_val = val
                    best_a = a
            if max_val == -float("inf"):
                max_val = 0
            self.stateUtilityAndPolicyDict[str(s)] = (round(state_reward + max_val, 2), best_a)
        # print_debug("")
        # self.printStatesDict()

    def runValueIteration(self, delta):
        print_debug("RUNNING VALUE ITERATION ALGORITHM:")
        iterations = 1
        start = timeit.default_timer()
        prev_dict = deepcopy(self.stateUtilityAndPolicyDict)
        self.ValueIteration()
        max_change = 0
        for s in self.all_possible_states:
            change = abs(self.stateUtilityAndPolicyDict[str(s)][0] - prev_dict[str(s)][0])
            if change > max_change:
                max_change = change
        while max_change >= delta:
            iterations += 1
            prev_dict = deepcopy(self.stateUtilityAndPolicyDict)
            self.ValueIteration()
            max_change = 0
            for s in self.all_possible_states:
                change = self.stateUtilityAndPolicyDict[str(s)][0] - prev_dict[str(s)][0]
                if change > max_change:
                    max_change = change
            # print_debug(str(max_change))
        stop = timeit.default_timer()
        print_debug("Took " + str(iterations) + " iterations, " + str(round(stop - start, 2)) +
                    " seconds.")
        print_debug("Utilities and best policy:")
        self.printStatesDict()

    def getBestPolicy(self, ag_state):
        """
        :type ag_state: AgentState
        """
        for s in self.all_possible_states:
            if s.compareToAgentState(ag_state):
                return self.stateUtilityAndPolicyDict[str(s)][1]
        raise Exception("No such state in dict" + str(ag_state))

    def printStatesDict(self):
        # sorted_all_states = sorted(self.all_possible_states, key=attrgetter('ag_loc', 'time'))
        for s in self.all_possible_states:
            print_debug(str(s) + "\t=\t" + str(self.stateUtilityAndPolicyDict[str(s)]))

    def update(self):
        agent = self.agent
        if agent.curr_state.is_terminated:
            return
        ag_location = agent.curr_state.curr_location
        agent.curr_state.v_people = self.get_people_array_considering_deadlines()
        if agent.hurricane_check():
            print_debug("AGENT " + str(agent) + " GOT HIT BY HURRICANE AT " + str(ag_location))
            ppl_on_agent = agent.terminate()
            self.reduce_agent_score(ppl_on_agent + self.k_value)
        else:
            if not agent.is_traversing():
                agent.at_vertex_auto_actions()
                agent.curr_state.v_people = self.get_people_array_considering_deadlines()
                self.set_agent_score(agent.curr_state.p_saved)
                agent_action = agent.action(self)
                # self.env_state = self.env_state.successor_fn_with_action(agent_action)
                if agent_action:
                    if agent_action == "TERMINATE":
                        ppl_on_agent = agent.terminate()
                        if ppl_on_agent > 0:
                            self.reduce_agent_score(ppl_on_agent + self.k_value)
                        elif not agent.curr_state.curr_location.is_shelter():
                            self.reduce_agent_score(self.k_value)
                    else:  # "TRAVERSE"
                        dest_e = None
                        dest_v = None
                        if agent_action[0] == 'E':
                            dest_e = self.graph.get_edge_from_string(agent_action)
                            if dest_e.vertex_1 == agent.curr_state.curr_location:
                                dest_v = dest_e.vertex_2
                            else:
                                dest_v = dest_e.vertex_1
                        elif agent_action[0] == 'V':
                            dest_v = self.graph.get_vertex_from_string(agent_action)
                            dest_e = self.graph.get_edge(agent.curr_state.curr_location, dest_v)
                        agent.traverse(dest_e, dest_v)
        agent.curr_state.time_update()

    def add_agent(self, s_vertex):
        index = 1
        initial_state = AgentState(s_vertex, self.graph.get_people_array(), self.k_value)
        ag = ValueIterationAgent(index, initial_state)
        print_info("ADDED AGENT TO ENVIRONMENT.")
        self.agent = ag

    def get_people_array_considering_deadlines(self):
        res = self.graph.get_people_array()
        for i in range(len(res)):
            if self.graph.vertices[i].deadline < self.env_state.time:
                res[i] = 0
        return res

    def add_agent_score(self, amount):
        self.agent_score += amount

    def reduce_agent_score(self, amount):
        self.agent_score -= amount

    def set_agent_score(self, amount):
        self.agent_score = amount

    def simulation(self):
        print("------------------------------------------------")
        self.initializeStatesDict()
        self.runValueIteration(Environment.VALUE_ITERATION_DELTA)
        dictCopy = deepcopy(self.stateUtilityAndPolicyDict)
        play = 'Y'
        while play == 'Y':
            self.stateUtilityAndPolicyDict = deepcopy(dictCopy)
            print_info("STARTING SIMULATION:")
            self.setRealEdgesStatus()
            self.add_agent(self.env_state.ag_loc)
            print_info("CREATED RANDOM INSTANCE OF ENVIRONMENT:")
            self.print_env()
            if not self.agent:
                self.print_env()
            else:
                ag = self.agent
                while not ag.curr_state.is_terminated:
                    if ag.is_traversing():
                        ag.traverse_update()
                    for v in self.graph.vertices:
                        if not v.is_shelter() and v.deadline < self.env_state.time:
                            self.dead_ppl += v.ppl_count
                            v.ppl_count = 0
                    print_debug("PRINTING ENVIRONMENT STATUS:")
                    self.print_changes()
                    print_debug("AGENTS OPERATING IN ENVIRONMENT:")
                    self.update()
                    print_debug("DONE WITH AGENTS OPERATING IN ENVIRONMENT.")
                    self.env_state.time += 1
                    print("------------------------------------------------")

            print_debug("GAME OVER")
            print_info("PRINTING ENVIRONMENT STATUS:")
            self.print_env()
            print_query("Play again? (Y/N)")
            play = input()
            self.graph = deepcopy(self.grapCopy)
            self.initEnvironmentVariables()

    def print_env(self):
        print_info("TIME IS: " + str(self.env_state.time))

        print_info("OUR VERTICES TYPES:")
        v_types = []
        for vertex in self.graph.vertices:
            v_types.append(vertex.v_type)
        print_info(str(v_types))

        print_info("OUR VERTICES DEADLINES:")
        deadlines = []
        for vertex in self.graph.vertices:
            deadlines.append(vertex.deadline)
        print_info(str(deadlines))

        print_info("OUR VERTICES PEOPLE COUNT: ")
        people_arr = self.graph.get_people_array_with_shelter()
        print_info(str(people_arr))

        print_info("OUR EDGES ACTUAL BLOCKAGE STATUS:")
        edges_actual_blockage_status = self.graph.get_edges_actual_blocked_status()
        print_info(str(edges_actual_blockage_status))

        ppl_saved = sum([v.ppl_count for v in self.graph.vertices if v.is_shelter()])
        print_info("PEOPLE SAVED: " + str(ppl_saved) + "/" + str(self.total_ppl))

        print_info("OUR AGENTS:")
        ag_names = []
        ag_states = []
        agent = self.agent
        ag_names.append(str(agent))
        ag_states.append(str(agent.curr_state))
        print_info("AGENTS: " + str(ag_names))
        print_info("AGENTS SCORES: " + str(self.agent_score))
        print_info("AGENTS STATES: " + str(ag_states))

    def print_changes(self):
        print_info("TIME IS: " + str(self.env_state.time))
        print_info("OUR VERTICES PEOPLE COUNT: ")
        people_arr = self.graph.get_people_array_with_shelter()
        print_info(str(people_arr))
        ppl_saved = sum([v.ppl_count for v in self.graph.vertices if v.is_shelter()])
        print_info("PEOPLE SAVED: " + str(ppl_saved) + "/" + str(self.total_ppl))
        print_info("AGENT STATE: " +str(str(self.agent.curr_state)))

