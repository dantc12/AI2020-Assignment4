from copy import deepcopy

from agent import Agent
from agent import ValueIterationAgent, AgentState
from graph import Graph
from helper_funcs import print_debug, print_info, print_query
from searchagents import GreedySearchAgent, AStarSearchAgent
from EnvState import EnvState


class Environment:

    PERCEPT = None
    K_DEFAULT_VALUE = 2

    def __init__(self, config_file_path, k_value=K_DEFAULT_VALUE):
        self.graph = Graph(config_file_path)
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

        print_debug("CREATED ENVIRONMENT WITH " + str(self.graph.num_of_vertices()) + " VERTICES, AND " +
                    str(self.graph.num_of_roads()) + " ROADS.")
        print_debug("ENVIRONMENT STARTING STATE: " + str(self.env_state))

        self.all_possible_states = []

        self.stateUtilityAndPolicyDict = {}

        ################## NEEDED? #################
        self.people1 = self.graph.get_vertex_from_string("V3")
        self.people2 = self.graph.get_vertex_from_string("V4")
        self.uncertain_edge = self.graph.get_edge_from_string("E3")
        self.uncertain_edge_status = False  # TODO:  do it randomly!

    #  Environment state is of the following structure:
    #  (AgentLocation, PeopleAtVertices?[], EdgesBlocked?[], CarryingCount, Time, SavedCount, Terminated?)

    ################## NEEDED? #################
    #  ---- total number of num_of_vertex * 2 * 2 * 4 * 3 * 7 * 3 * 2 = 10,080 possible states
    def generateUncertaintyTable(self, deadline_time=7):
        pass
        # # bool = [True, False]
        # # edge_stats = [True, False, -1]
        #
        # vertex_options = self.graph.vertices
        #
        # people_vertices = self.graph.get_people_vertices()
        # people_at_vertex_options = Environment.TrueFalseArrayCombinations(len(people_vertices))
        #
        # poss_blocked_edges = self.graph.get_poss_blocked_edges()
        # blocked_edges_options = Environment.TrueFalseArrayCombinations(len(poss_blocked_edges))
        #
        # possiblePeople = self.possiblePeopleCombinations()
        # for vertex in self.graph.vertices:
        #     for people_1 in bool:
        #         for people_2 in bool:
        #             for num_carry in possiblePeople:
        #                 for edge_stat in edge_stats:
        #                     for time in range(1,deadline_time+1):
        #                         for num_saved in possiblePeople:
        #                             for terminated in bool:
        #                                 self.stateDict[(vertex, people_1, people_2, num_carry, edge_stat, time, num_saved, terminated)] = ["possible actions", "value", "best"]

    ################## NEEDED? #################
    def getPossibleActions(self, state):
        pass
        # actions_list = []
        # additional_people = 0
        # vertex, people_1, people_2, num_carry, edge_stat, time, num_saved, terminated = state
        # current_vertext = self.graph.get_vertex_from_string("V" + vertex)
        # vertices_with_weights = current_vertext.get_connected_vertices_with_weights()
        # for neihgbor in vertices_with_weights:
        #     curr_edge = self.graph.get_edge(neihgbor[0], current_vertext)
        #     if curr_edge.__eq__(self.uncertain_edge):
        #         if uncertain_edge_status is False:
        #             continue  # Edge is blocked
        #         if uncertain_edge_status is -1:
        #             edge_stat = uncertain_edge_status
        #
        #     if neihgbor[0].__eq__(self.people1):
        #         additional_people = neihgbor[0].pick_up()
        #         people_1 = 0
        #     if neihgbor[0].__eq__(self.people2):
        #         additional_people = neihgbor[0].pick_up()
        #         people_2 = 0
        #     num_carry += additional_people
        #     if neihgbor[0].is_shelter():
        #         num_saved += num_carry
        #         num_carry = 0
        #
        #     currState = (neihgbor[0], people_1, people_2, num_carry, edge_stat, time + neihgbor[1], num_saved, False)
        #     currState = self.graph.is_mpd_terminate(currState)  # TODO: implement termination check
        #     actions_list.append(currState)

    #  returns all the people combinations for example for people in 2 vertices {1,2} return {0, 1, 2, 3
    def possiblePeopleCombinations(self, prefix):
        # possabilities = []
        # possabilities.append(0)
        # for vertex in self.graph.vertices:
        #     if vertex.ppl_count > 0:
        #         people_in_vertices.append(vertex.ppl_count)
        #
        # combinations = list(combinations(range(len(people_in_vertices)-1)))
        # for combination in combinations:
        #     num_of_people = 0
        #     for item in combination:
        #         num_of_people += people_in_vertices[int(item)]
        #     possabilities.append(num_of_people)
        # return possabilities
        pass

    def initializeStatesDict(self):
        self.all_possible_states = self.env_state.getAllPossibleStates()
        print_debug(len(self.all_possible_states))
        print_debug("")
        for s in self.all_possible_states:
            self.stateUtilityAndPolicyDict[str(s)] = (0, "")
        self.printStatesDict()
        print_debug("")

    def ValueIteration(self):
        for s in self.all_possible_states:
            state_reward = -1
            if s.ag_loc.is_shelter() and s.prev_state.carrying_count > 0:
                state_reward += s.prev_state.carrying_count
            max_val = -float("inf")
            best_a = ""
            for a in s.get_pos_actions():
                res_states = s.successor_fn_with_action(a)
                val = 0
                for res_state in res_states:
                    val += self.stateUtilityAndPolicyDict[str(res_state)][0] * s.T(res_state)
                if val > max_val:
                    max_val = val
                    best_a = a

            self.stateUtilityAndPolicyDict[str(s)] = (state_reward + max_val, best_a)
        # self.printStatesDict()

    def runValueIteration(self, delta):
        iterations = 1
        prev_dict = deepcopy(self.stateUtilityAndPolicyDict)
        self.ValueIteration()
        max_change = 0
        for s in self.all_possible_states:
            change = self.stateUtilityAndPolicyDict[str(s)][0] - prev_dict[str(s)][0]
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
        self.printStatesDict()
        print_debug(str(max_change))
        print_debug(str(iterations))

    def printStatesDict(self):
        for s in self.all_possible_states:
            print_debug(str(s) + ": " + str(self.stateUtilityAndPolicyDict[str(s)]))

    # TODO
    def update(self):
        agent = self.agent
        if agent.curr_state.is_terminated:
            return
        ag_location = agent.curr_state.curr_location
        agent.curr_state.v_people = self.get_people_array_considering_deadlines()
        if agent.hurricane_check():
            print_debug("AGENT " + str(agent) + " GOT HIT BY HURRICANE AT " + str(ag_location))
            ppl_on_agent = agent.terminate()
            self.reduce_agent_score(agent, ppl_on_agent + self.k_value)
        else:
            if not agent.is_traversing():
                agent.at_vertex_auto_actions()
                agent.curr_state.v_people = self.get_people_array_considering_deadlines()
                self.set_agent_score(agent, agent.curr_state.p_saved)
                agent_action = agent.action(self)
                if agent_action:
                    if agent_action == "TERMINATE":
                        ppl_on_agent = agent.terminate()
                        if ppl_on_agent > 0:
                            self.reduce_agent_score(agent, ppl_on_agent + self.k_value)
                        elif not agent.curr_state.curr_location.is_shelter():
                            self.reduce_agent_score(agent, self.k_value)
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
            if self.graph.vertices[i].deadline < self.env_time:
                res[i] = 0
        return res

    def add_agent_score(self, agent, amount):
        self.agent_scores[agent.index-1] = self.agent_scores[agent.index-1] + amount

    def reduce_agent_score(self, agent, amount):
        self.agent_scores[agent.index-1] = self.agent_scores[agent.index-1] - amount

    def set_agent_score(self, agent, amount):
        self.agent_scores[agent.index-1] = amount

    def simulation(self):
        #### DEBUGGING ######
        self.initializeStatesDict()
        self.runValueIteration(0.3)
        # if not self.agent:
        #     self.print_env()
        # else:
        #     ag = self.agent
        #     while not ag.curr_state.is_terminated:
        #         if ag.is_traversing():
        #             ag.traverse_update()
        #         for v in self.graph.vertices:
        #             if not v.is_shelter() and v.deadline < self.env_state.time:
        #                 self.dead_ppl += v.ppl_count
        #                 v.ppl_count = 0
        #         print_debug("PRINTING ENVIRONMENT STATUS:")
        #         self.print_env()
        #         print_debug("AGENTS OPERATING IN ENVIRONMENT:")
        #         self.update()
        #         print_debug("DONE WITH AGENTS OPERATING IN ENVIRONMENT.")
        #
        #         # print_info("PRESS ENTER FOR NEXT PHASE...")
        #         # raw_input()
        #         self.env_state.time += 1
        #         print "------------------------------------------------"
        #
        # print_debug("GAME OVER")
        # print_info("PRINTING ENVIRONMENT STATUS:")
        # self.print_env()


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

