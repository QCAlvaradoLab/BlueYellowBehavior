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
            attach_legend = job.get(const.ATTACH_LEGEND)

            print('Now processing job #{}: {}'.format(idx + 1, job_title))
            data = BehaviorTransitionData(input_folder, output_folder, subject, env, color_map, group_by)
            data.create_markov_chain_graph(attach_legend)

        print(f'All {len(jobs)} job(s) have been processed. Check specified output folder for results.')
    except Exception as e:
        print(e)


def main_alt():
    input = 'AllFightClubScorelogs'
    output = 'outputs/final_drafts/draft_8'
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
        'ATTACK_BLUE': '#bd3977', # Aggressive
        'ATTACK_YELLOW': '#ff00f0', # Aggressive
        'ATTACK_\\U2640': '#a4133c', # Aggressive
        'BLUE_LATERAL_DISPLAY': '#e36602', # Aggressive
        'CHASE_\\U2640': '#ff4d6d', # Aggressive
        'CHASE_\\U2642': '#FF758F', # Aggressive
        'DIG': '#e5e84a', # Reproductive
        'FLEE_FROM_\\U2640': '#1d92cc', # Aversive
        'FLEE_FROM_\\U2642': '#370fbf', # Aversive
        'FRONTAL_DISPLAY': '#b36042', # Aggressive
        'LEAD_SWIM': '#c7c92c', # Reproductive
        'POT_ENTRY': '#f8fc03', # Reproductive
        'POT_EXIT': '#828501', # Reproductive
        'QUIVER_AT_\\U2640': '#fcfdbf', # Reproductive
        'QUIVER_AT_\\U2642': '#ff005c', # Aggressive
        'YELLOW_LATERAL_DISPLAY': '#ffccd5', # Aggressive
        'DEFAULT': 'white'
    }
    behaviorsByCategory = BehaviorTransitionData('BlueFishCategorical', output, 'Blue', '', color_map, 'BEHAVIORAL_CATEGORY')
    behaviorsByCategory.create_markov_chain_graph(attach_legend=False)
    behaviorsByCategory = BehaviorTransitionData('YellowFishCategorical', output, 'Yellow', '', color_map, 'BEHAVIORAL_CATEGORY')
    behaviorsByCategory.create_markov_chain_graph(attach_legend=False)




if __name__ == '__main__':
    main_alt()