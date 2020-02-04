from environment import Environment as Env
from helper_funcs import print_debug, print_query, print_info

ENVIRONMENT_SETTINGS_FILE = "environment_settings1.txt"

print_query("Please enter K vehicle loss penalty value:")
# inp = raw_input()
inp = ''
if str(inp) == '':
    env = Env(ENVIRONMENT_SETTINGS_FILE)
else:
    env = Env(ENVIRONMENT_SETTINGS_FILE, int(inp))


print_info("OUR GRAPH:")
print_info(env.graph)

s_vertex = env.graph.vertices[0]
env.add_agent(s_vertex)

print "------------------------------------------------"
print_debug("STARTING SIMULATION:")
env.simulation()
