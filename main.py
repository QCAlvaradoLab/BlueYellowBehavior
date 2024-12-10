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
    output = 'outputs/final_drafts/draft_7'
    color_map = {
        'BITE': '#b52dc8',#'#6817C5',
        'HEAD_TO_HEAD': '#1565C0',
        'LATERAL_DISPLAY': '#009688',
        'FLEE': '#709c3e',#'#55782c',#'#8BC34A',
        'FORAGING': '#AD1457',
        'POT_ENTRY/EXIT': '#bf9502',#'#a68100',#'#E85D04',#'#6817C5',
        'CHASE': '#F44336',#'#3d3d3d',
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
        'ATTACK_BLUE': '#590D22', # Aggressive
        'ATTACK_YELLOW': '#800F2F', # Aggressive
        'ATTACK_\\U2640': '#A4133C', # Aggressive
        'BLUE_LATERAL_DISPLAY': '#C9184A', # Aggressive
        'CHASE_\\U2640': '#FF4D6D', # Aggressive
        'CHASE_\\U2642': '#FF758F', # Aggressive
        'DIG': '#007F5F', # Reproductive
        'FLEE_FROM_\\U2640': '#00B4D8', # Aversive
        'FLEE_FROM_\\U2642': '#0077B6', # Aversive
        'FRONTAL_DISPLAY': '#FF8FA3', # Aggressive
        'LEAD_SWIM': '#55A630', # Reproductive
        'POT_ENTRY': '#AACC00', # Reproductive
        'POT_EXIT': '#2B9348', # Reproductive
        'QUIVER_AT_\\U2640': '#80B918', # Reproductive
        'QUIVER_AT_\\U2642': '#FFB3C1', # Aggressive
        'YELLOW_LATERAL_DISPLAY': '#FFCCD5', # Aggressive
        'DEFAULT': 'white'
    }
    behaviorsByCategory = BehaviorTransitionData('BlueFishCategorical', output, 'Blue', '', color_map, 'BEHAVIORAL_CATEGORY')
    behaviorsByCategory.create_markov_chain_graph(attach_legend=False)
    behaviorsByCategory = BehaviorTransitionData('YellowFishCategorical', output, 'Yellow', '', color_map, 'BEHAVIORAL_CATEGORY')
    behaviorsByCategory.create_markov_chain_graph(attach_legend=False)




if __name__ == '__main__':
    main_alt()