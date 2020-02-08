from environment import Environment as Env
from helper_funcs import print_query, print_info

ENVIRONMENT_SETTINGS_FILE = "environment_settings_test.txt"

# print_query("Please enter K vehicle loss penalty value:")
# inp = raw_input()
inp = ''
if str(inp) == '':
    env = Env(ENVIRONMENT_SETTINGS_FILE)
else:
    env = Env(ENVIRONMENT_SETTINGS_FILE, int(inp))

env.simulation()
