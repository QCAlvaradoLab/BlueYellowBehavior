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

        config = object()
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
    input = 'AllFightClubScorelogs/BlueFishinBlue'
    output = 'outputs/output8'
    subject = 'Blue'
    env = 'Blue'
    color_map = {
        'BITE': 'aqua',
        'HEAD_TO_HEAD': 'chartreuse',
        'LATERAL_DISPLAY': 'cornflowerblue',
        'FLEE': 'darksalmon',
        'FORAGING': 'deeppink',
        'POT_ENTRY/EXIT': 'gold2',
        'CHASE': 'firebrick1',
        'DEFAULT': 'antiquewhite'
    }
    # behaviors = BehaviorTransitionData(input, output, subject, env, color_map)
    # behaviors.create_markov_chain_graph(attach_legend=False)

    # behaviors2 = BehaviorTransitionData(input, output, subject, env, color_map, 'TIME')
    # behaviors2.create_markov_chain_graph(attach_legend=False)

    input = 'BlueFishCategorical'
    output = 'outputs/categorical_output22'

    color_map = {
        'ATTACK_BLUE': 'aqua',
        'ATTACK_YELLOW': 'chartreuse',
        'ATTACK_\\U2640': '#7f03fc',
        'BLUE_LATERAL_DISPLAY': 'cornflowerblue',
        'CHASE_\\U2640': 'firebrick1',
        'CHASE_\\U2642': '#fcba03',
        'DIG': 'darksalmon',
        'FLEE_FROM_\\U2640': '#88fc03',
        'FLEE_FROM_\\U2642': '#6eb8b8',
        'FRONTAL_DISPLAY': 'deeppink',
        'LEAD_SWIM': 'gold2',
        'POT_ENTRY': '#b8906e',
        'POT_EXIT': '#8a694c',
        'QUIVER_AT_\\U2640': '#c4be97',
        'QUIVER_AT_\\U2642': '#7a765d',
        'YELLOW_LATERAL_DISPLAY': '#c9b849',
        'DEFAULT': 'white'
    }

    # behaviors3 = BehaviorTransitionData(input, output, subject, '', color_map, const.BEHAVIORAL_CATEGORY)
    # behaviors3.create_markov_chain_graph(attach_legend=False)
    # behaviors3.output_dfs_as_csvs()



if __name__ == '__main__':
    main_alt()