import sys
import getopt
import json

from utils.helper_utils import format_json_input, BehaviorTransitionData
from utils import constants as const


# Script usage: python3 main.py <ConfigFilePath>
def main():
    try:
        argv = sys.argv[1:]
        if len(argv) != 1:
            raise Exception()

        config = dict()
        with open(argv[0]) as file:
            config = json.load(file)
            config = format_json_input(config)

        print('Job processing has started')
        jobs = config.get(const.JOBS)
        for idx, job in enumerate(jobs):
            job_title = job.get(const.JOB_TITLE) or None
            input_folder = job.get(const.INPUT_FOLDER)
            output_folder = job.get(const.OUTPUT_FOLDER)
            subject = job.get(const.SUBJECT)
            env = job.get(const.ENV)
            color_map = job.get(const.COLOR_MAP)
            group_by = job.get(const.GROUP_BY)
            attach_legend = job.get(const.ATTACH_LEGEND) or False

            print('Now processing job #{}: {}'.format(idx + 1, job_title))
            data = BehaviorTransitionData(input_folder, output_folder, subject, env, color_map, group_by)
            data.create_markov_chain_graph(attach_legend)

        print(f'All {len(jobs)} job(s) have been processed. Check specified output folder for results.')
    except Exception as e:
        print(e)


def main_alt():
    input = 'some/input/folder'
    output = 'some/output/folder'
    color_map = {
        'BITE': '#481567',
        'HEAD_TO_HEAD': '#4179ab',
        'LATERAL_DISPLAY': '#2aea8f',
        'FLEE': '#73d05f',
        'FORAGING': '#7f4dc4',
        'POT_ENTRY/EXIT': '#b8de29',
        'CHASE': '#238a8d',
        'DEFAULT': 'white'
    }

    # Behavior Transition Graphs
    behaviors = BehaviorTransitionData(f'{input}/BlueFishinBlue', output, 'Blue', 'Blue', color_map)
    behaviors.create_markov_chain_graph(attach_legend=False)
    behaviors = BehaviorTransitionData(f'{input}/BlueFishinYellow', output, 'Blue', 'Yellow', color_map)
    behaviors.create_markov_chain_graph(attach_legend=False)
    behaviors = BehaviorTransitionData(f'{input}/YellowFishinBlue', output, 'Yellow', 'Blue', color_map)
    behaviors.create_markov_chain_graph(attach_legend=False)
    behaviors = BehaviorTransitionData(f'{input}/YellowFishinYellow', output, 'Yellow', 'Yellow', color_map)
    behaviors.create_markov_chain_graph(attach_legend=False)

    # Behavior Transition Graphs (split by hour)
    behaviorsByTime = BehaviorTransitionData(f'{input}/BlueFishinBlue', output, 'Blue', 'Blue', color_map, 'TIME')
    behaviorsByTime.create_markov_chain_graph(attach_legend=False)
    behaviorsByTime = BehaviorTransitionData(f'{input}/BlueFishinYellow', output, 'Blue', 'Yellow', color_map, 'TIME')
    behaviorsByTime.create_markov_chain_graph(attach_legend=False)
    behaviorsByTime = BehaviorTransitionData(f'{input}/YellowFishinBlue', output, 'Yellow', 'Blue', color_map, 'TIME')
    behaviorsByTime.create_markov_chain_graph(attach_legend=False)
    behaviorsByTime = BehaviorTransitionData(f'{input}/YellowFishinYellow', output, 'Yellow', 'Yellow', color_map, 'TIME')
    behaviorsByTime.create_markov_chain_graph(attach_legend=False)

    # Behavior Transition Graphs (nodes grouped by category)
    color_map = {
        'ATTACK_BLUE': '#0000a8', # Aggressive
        'ATTACK_YELLOW': '#ff2e00', # Aggressive
        'ATTACK_\\U2640': '#d23105', # Aggressive
        'BLUE_LATERAL_DISPLAY': '#edfa11', # Aggressive
        'CHASE_\\U2640': '#73090e', # Aggressive
        'CHASE_\\U2642': '#FF758F', # Aggressive
        'DIG': '#f8bc39', # Reproductive
        'FLEE_FROM_\\U2640': '#4670e7', # Aversive
        'FLEE_FROM_\\U2642': '#75fe5c', # Aversive
        'FRONTAL_DISPLAY': '#fa7e21', # Aggressive
        'LEAD_SWIM': '#b3ff4b', # Reproductive
        'POT_ENTRY': '#bbf534', # Reproductive
        'POT_EXIT': '#2cb6ef', # Reproductive
        'QUIVER_AT_\\U2640': '#3c3387', # Reproductive
        'QUIVER_AT_\\U2642': '#42f687', # Aggressive
        'YELLOW_LATERAL_DISPLAY': '#31133e', # Aggressive
        'DEFAULT': 'white'
    }
    behaviorsByCategory = BehaviorTransitionData('BlueFishCategorical', output, 'Blue', '', color_map, 'BEHAVIORAL_CATEGORY')
    behaviorsByCategory.create_markov_chain_graph(attach_legend=False)
    behaviorsByCategory = BehaviorTransitionData('YellowFishCategorical', output, 'Yellow', '', color_map, 'BEHAVIORAL_CATEGORY')
    behaviorsByCategory.create_markov_chain_graph(attach_legend=False)




if __name__ == '__main__':
    main_alt()