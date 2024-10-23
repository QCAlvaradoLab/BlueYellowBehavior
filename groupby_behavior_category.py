import os
import math

from graphviz.graphs import Digraph
import pandas as pd
import graphviz as gv
import numpy as np

import utils.constants as const
from utils.helper_utils import upper_snake

type FNameToDFrameDict = dict[str, pd.DataFrame]
def import_data(dir_path: str, columns: list[str] = []) -> FNameToDFrameDict:
    """
    Import data as a dictionary of dataframes
    columns = []
    """
    df: FNameToDFrameDict = dict()
    filenames = [filename for filename in os.listdir(dir_path) if filename.endswith(".csv") or filename.endswith(".tsv")]
    for filename in filenames:
        name, ext = filename.split(".")
        if ext == "csv":
            temp_df = pd.read_csv(os.path.join(dir_path, filename))
            df[name] = pd.DataFrame(temp_df[columns]) if len(columns) else temp_df.copy()
        elif ext == "tsv":
            temp_df = pd.read_csv(os.path.join(dir_path, filename), sep="\t")
            df[name] = pd.DataFrame(temp_df[columns]) if len(columns) else temp_df.copy()
    return df


def format_data(df_map: FNameToDFrameDict) -> tuple[pd.DataFrame, pd.DataFrame]:
    transition_dict: FNameToDFrameDict = {}
    behavior_dict: FNameToDFrameDict = {}
    for i, (name, sub_df) in enumerate(df_map.items()):
        sub_transition = pd.DataFrame()
        sub_behavior = pd.DataFrame()

        sub_transition['BEHAVIOR'] = sub_df['Behavior'].map(lambda x: '_'.join((str(x).upper().split(' '))))
        t_idx_label = sub_transition[sub_transition['BEHAVIOR'] == 'OUT_OF_VIEW'].index
        sub_transition.drop(t_idx_label, inplace=True)
        # sub_behavior['BEHAVIOR'] = sub_df['Behavior'].map(lambda x: '_'.join((str(x).upper().split(' '))))
        sub_behavior['BEHAVIOR'] = sub_transition['BEHAVIOR'].copy()

        sub_transition['BEHAVIOR_NEXT'] = sub_transition['BEHAVIOR'].shift(-1)
        # sub_transition['BEHAVIOR_NEXT'] = sub_df['Behavior'].shift(-1).map(lambda x: str(x).upper())

        time_next = sub_df['Time'].shift(-1)
        sub_transition['BEHAVIOR_DURATION'] = time_next - sub_df['Time']
        sub_behavior['BEHAVIOR_DURATION'] = time_next - sub_df['Time']

        transition_dict[name] = sub_transition.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT']).count()
        transition_dict[name].rename(columns={ 'BEHAVIOR_DURATION': 'TRANSITION_COUNTS'}, inplace=True)

        behavior_dict[name] = sub_behavior.groupby(['BEHAVIOR']).count()
        behavior_dict[name].rename(columns={ 'BEHAVIOR_DURATION': 'BEHAVIOR_COUNTS' }, inplace=True)


    transition_df = pd.concat(transition_dict.values(), sort=False)
    transition_df.fillna(0, inplace=True)
    transition_df = pd.DataFrame(transition_df.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT']).sum())
    transition_df.reset_index(level=[0, 1], inplace=True)

    # print(transition_df.keys)
    # transition_grouped = transition_df.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT'])
    # transition_df['AVG_TRANSITION_COUNTS'] = transition_grouped['TRANSITION_COUNTS'].transform('mean')
    # transition_df['STDERR_TRANSITION_COUNTS'] = transition_grouped['TRANSITION_COUNTS'].transform('sem')

    # transition_df['TRANSITION_PROBABILITY'] = transition_df['TRANSITION_COUNTS'] / transition_df.groupby(['BEHAVIOR']).sum()
    transition_df['BEHAVIOR_TOTALS'] = transition_df.groupby(['BEHAVIOR'])[['TRANSITION_COUNTS']].transform('sum')
    transition_df['TRANSITION_PROBABILITY'] = transition_df['TRANSITION_COUNTS'] / transition_df['BEHAVIOR_TOTALS']
    # transition_df['TRANSITION_PROBABILITY'] = transition_df['TRANSITION_COUNTS'] / transition_df['TRANSITION_COUNTS'].sum()
    # transition_df['AVG_TRANSITION_PROBABILITY'] = transition_grouped['TRANSITION_PROBABILITY'].transform('mean')
    # transition_df['STDERR_TRANSITION_PROBABILITY'] = transition_grouped['TRANSITION_PROBABILITY'].transform('sem')


    behavior_df = pd.concat(behavior_dict.values(), sort=False)
    behavior_df.fillna(0, inplace=True)
    behavior_df = pd.DataFrame(behavior_df.groupby(['BEHAVIOR']).sum())
    behavior_df.reset_index(level=[0], inplace=True)

    # behavior_grouped = behavior_df.groupby(['BEHAVIOR'])
    # behavior_df['AVG_BEHAVIOR_COUNTS'] = behavior_grouped['BEHAVIOR_COUNTS'].transform('mean')
    # behavior_df['STDERR_BEHAVIOR_COUNTS'] = behavior_grouped['BEHAVIOR_COUNTS'].transform('sem')

    behavior_df['BEHAVIOR_PROBABILITY'] = behavior_df['BEHAVIOR_COUNTS'] / behavior_df['BEHAVIOR_COUNTS'].sum()
    # behavior_df['BEHAVIOR_PROBABILITY'] = behavior_df['AVG_BEHAVIOR_COUNTS'] / behavior_df['AVG_BEHAVIOR_COUNTS'].sum()
    # behavior_df['AVG_BEHAVIOR_PROBABILITY'] = behavior_grouped['BEHAVIOR_PROBABILITY'].transform('mean')
    # behavior_df['STDERR_BEHAVIOR_PROBABILITY'] = behavior_grouped['BEHAVIOR_PROBABILITY'].transform('sem')


    return (transition_df, behavior_df)


type Subject = str
type EnvColor = str
type FishToDFrameDict = dict[Subject, dict[EnvColor, tuple[pd.DataFrame, pd.DataFrame]]]
def get_fish_dfs(
    root_dir: str,
    fish_types: list[Subject] = [],
    env_colors: list[EnvColor] = [],
    columns: list[str] = []
) -> FishToDFrameDict:
    df: FishToDFrameDict = dict()
    data_path = os.path.join(os.getcwd(), root_dir)

    for ft in fish_types:
        df[ft] = dict()
        for ec in env_colors:
            df_map = import_data(os.path.join(data_path, f'{ft}Fishin{ec}'), columns)
            df[ft][ec] = format_data(df_map)

    return df

color_map = {
    'BITE':'aqua',
    'HEAD_TO_HEAD':'chartreuse',
    'LATERAL_DISPLAY':'cornflowerblue',
    'FLEE':'darksalmon',
    'FORAGING':'deeppink',
    'POT_ENTRY/EXIT':'gold2',
    'CHASE': 'firebrick1',
    'DEFAULT': 'antiquewhite'
}

def create_markov_chains_categorical(root_dir: str, prob_threshold = 0.005):
    fish_dfs = get_fish_dfs(root_dir, ['Blue'])


# def format_data_categorically(df_map: dict[str, pd.DataFrame], group_by: str = '') -> tuple[pd.DataFrame, pd.DataFrame]:
#     transitions = {}
#     behaviors = {}
#     for idx, (name, sub_df) in enumerate(df_map.items()):
#         sub_transition = pd.DataFrame()
#         sub_behavior = pd.DataFrame()

#         sub_transition[const.BEHAVIOR] = sub_df['Behavior'].map(lambda x: upper_snake(str(x)))
#         if group_by == const.BEHAVIORAL_CATEGORY:
#             sub_transition[const.BEHAVIORAL_CATEGORY] = sub_df['Behavioral category'].map(lambda x: upper_snake(str(x)))

#         t_idx_label = sub_transition[sub_transition['BEHAVIOR'] == 'OUT_OF_VIEW'].index
#         # You can ignore the generated warning below. The above variable works fine as an argument
#         sub_transition.drop(t_idx_label, inplace=True)

#         sub_behavior['BEHAVIOR'] = sub_transition['BEHAVIOR'].copy()
#         if group_by == const.BEHAVIORAL_CATEGORY:
#             sub_behavior[const.BEHAVIORAL_CATEGORY] = sub_transition[const.BEHAVIORAL_CATEGORY].copy()

#         sub_transition['BEHAVIOR_NEXT'] = sub_transition['BEHAVIOR'].shift(-1)

#         # comment line below when we figure out minutes to seconds conversions
#         sub_df['Time'] = sub_df['Time'].map(lambda _: 1)
#         time_next = sub_df['Time'].shift(-1)
#         sub_transition['BEHAVIOR_DURATION'] = time_next - sub_df['Time']
#         sub_behavior['BEHAVIOR_DURATION'] = time_next = sub_df['Time']

#         if group_by == 'TIME':
#             sub_behavior['HOUR_PERFORMED'] = sub_df['Time'].transform(lambda x: math.ceil(x / 3600))
#             sub_transition['HOUR_PERFORMED'] = sub_df['Time'].transform(lambda x: math.ceil(x / 3600))

#             transitions[name] = sub_transition.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT', 'HOUR_PERFORMED']).count()
#             # transitions[name].rename(columns={ 'BEHAVIOR_DURATION': 'TRANSITION_COUNTS' }, inplace=True)

#             behaviors[name] = sub_behavior.groupby(['BEHAVIOR', 'HOUR_PERFORMED']).count()
#             # behaviors[name].rename(columns={ 'BEHAVIOR_DURATION': 'BEHAVIOR_COUNTS' }, inplace=True)
#         elif group_by == 'BEHAVIORAL_CATEGORY':
#             transitions[name] = sub_transition.groupby([const.BEHAVIOR, const.BEHAVIOR_NEXT, const.BEHAVIORAL_CATEGORY]).count()
#             behaviors[name] = sub_behavior.groupby([const.BEHAVIOR, const.BEHAVIORAL_CATEGORY]).count()
#         else:
#             transitions[name] = sub_transition.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT']).count()
#             # transitions[name].rename(columns={ 'BEHAVIOR_DURATION': 'TRANSITION_COUNTS' }, inplace=True)

#             behaviors[name] = sub_behavior.groupby(['BEHAVIOR']).count()
#             behaviors[name].rename(columns={ 'BEHAVIOR_DURATION': 'BEHAVIOR_COUNTS' }, inplace=True)

#         transitions[name].rename(columns={ 'BEHAVIOR_DURATION': 'TRANSITION_COUNTS' }, inplace=True)
#         behaviors[name].rename(columns={ 'BEHAVIOR_DURATION': 'BEHAVIOR_COUNTS' }, inplace=True)

#     transition_dataframe = pd.concat(transitions.values(), sort=False)
#     transition_dataframe.fillna(0, inplace=True)

#     behavior_dataframe = pd.concat(behaviors.values(), sort=False)
#     behavior_dataframe.fillna(0, inplace=True)
#     # print(behavior_dataframe)

#     if group_by == const.TIME:
#         transition_dataframe = pd.DataFrame(transition_dataframe.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT', 'HOUR_PERFORMED']).sum())
#         transition_dataframe.reset_index(level=[0, 1, 2], inplace=True)

#         behavior_dataframe = pd.DataFrame(behavior_dataframe.groupby(['BEHAVIOR', 'HOUR_PERFORMED']).sum())
#         behavior_dataframe.reset_index(level=[0, 1], inplace=True)

#         transition_dataframe['BEHAVIOR_TOTALS'] = transition_dataframe.groupby(['BEHAVIOR', 'HOUR_PERFORMED'])[['TRANSITION_COUNTS']].transform('sum')
#         transition_dataframe['TRANSITION_PROBABILITY'] = transition_dataframe['TRANSITION_COUNTS'] / transition_dataframe['BEHAVIOR_TOTALS']

#         behavior_dataframe['BEHAVIOR_TOTALS_BY_HOUR'] = behavior_dataframe.groupby(['HOUR_PERFORMED'])[['BEHAVIOR_COUNTS']].transform('sum')
#         behavior_dataframe['BEHAVIOR_PROBABILITY'] = behavior_dataframe['BEHAVIOR_COUNTS'] / behavior_dataframe['BEHAVIOR_TOTALS_BY_HOUR']
#     elif group_by == const.BEHAVIORAL_CATEGORY:
#         transition_dataframe = pd.DataFrame(transition_dataframe.groupby([const.BEHAVIOR, const.BEHAVIOR_NEXT, const.BEHAVIORAL_CATEGORY]).sum())
#         transition_dataframe.reset_index(level=[0, 1, 2], inplace=True)

#         behavior_dataframe = pd.DataFrame(behavior_dataframe.groupby([const.BEHAVIOR, const.BEHAVIORAL_CATEGORY]).sum())
#         behavior_dataframe.reset_index(level=[0, 1], inplace=True)

#         transition_dataframe['BEHAVIOR_TOTALS'] = transition_dataframe.groupby([const.BEHAVIOR, const.BEHAVIORAL_CATEGORY])[['TRANSITION_COUNTS']].transform('sum')
#         transition_dataframe['TRANSITION_PROBABILITY'] = transition_dataframe['TRANSITION_COUNTS'] / transition_dataframe['BEHAVIOR_TOTALS']

#         behavior_dataframe['BEHAVIOR_PROBABILITY'] = behavior_dataframe['BEHAVIOR_COUNTS'] / behavior_dataframe['BEHAVIOR_COUNTS'].sum()
#     else:
#         transition_dataframe = pd.DataFrame(transition_dataframe.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT']).sum())
#         transition_dataframe.reset_index(level=[0, 1], inplace=True)

#         behavior_dataframe = pd.DataFrame(behavior_dataframe.groupby(['BEHAVIOR']).sum())
#         behavior_dataframe.reset_index(level=[0], inplace=True)

#         transition_dataframe['BEHAVIOR_TOTALS'] = transition_dataframe.groupby(['BEHAVIOR'])[['TRANSITION_COUNTS']].transform('sum')
#         transition_dataframe['TRANSITION_PROBABILITY'] = transition_dataframe['TRANSITION_COUNTS'] / transition_dataframe['BEHAVIOR_TOTALS']

#         behavior_dataframe['BEHAVIOR_PROBABILITY'] = behavior_dataframe['BEHAVIOR_COUNTS'] / behavior_dataframe['BEHAVIOR_COUNTS'].sum()

#     return (transition_dataframe, behavior_dataframe)


def create_markov_chains(root_dir: str, prob_threshold = 0.05):
    fish_dfs = get_fish_dfs(root_dir, ['Blue', 'Yellow'], ['Blue', 'Yellow'])

    for (fish, env_dfs) in fish_dfs.items():
        for (env, (trans_dfs, behave_dfs)) in env_dfs.items():
            g = gv.Digraph(f'{fish} Fish Behaviors in {env} Colored Environment')
            bgcolor = '#FFFFCC' if env == 'Yellow' else '#CCFFFF'
            g.attr(overlap='scale',
                # size='7,3!',
                # ratio='fill',
                # dpi='300',
                size='50',
                bgcolor=bgcolor, fontcolor='black',
                packMode='graph', label=f'{fish} Fish in {env} Env: Transition Probability >{prob_threshold * 100}%',
                fontname='fira-code', labelloc='t', cluster='true', rankdir='LR')

            behavior_legend_keys: list[str] = []
            for idx, row in behave_dfs.iterrows():
                behavior_name = str(row['BEHAVIOR'])
                color_to_use = color_map[behavior_name] if color_map[behavior_name] is not None else color_map['DEFAULT']
                prob = np.round(row['BEHAVIOR_PROBABILITY'] * 100, 1)

                node_size = constrain_value(row['BEHAVIOR_PROBABILITY'] * 10, 0.5, 3)
                g.node(f'{behavior_name}', color=color_to_use,
                    # label=f"{behavior_name}\n{prob}%",
                    # label=f"{prob}%",
                    label=' ',
                    fontcolor='black',
                    # height=str(row['BEHAVIOR_PROBABILITY']),
                    shape='circle',
                    style='filled', width=str(node_size))

                behavior_legend_keys.append(f"{behavior_name} {prob}")

            for idx, row in trans_dfs.iterrows():
                behavior_name = str(row['BEHAVIOR'])
                scaled = constrain_value(20*row['TRANSITION_PROBABILITY'], 1, 10)
                weight = np.round(row['TRANSITION_PROBABILITY'] * 100, 1)
                color_to_use = color_map[behavior_name] if color_map.get(behavior_name) is not None else color_map['DEFAULT']

                if weight < prob_threshold * 100:
                    continue
                g.edge(f'{behavior_name}', f'{row['BEHAVIOR_NEXT']}',
                    color=color_to_use, #label=f'{str(weight)}%', labelloc='c',
                    # fontsize='15',
                    penwidth=str(scaled), fontcolor='white')
            # sub_g = g.subgraph(name=f'{env} Colored Environment')
            # assert sub_g is not None
            # with sub_g as c:
                # c.attr(label=f'{fish}_{env}', fontname='fira-code', labelloc='b', color='black')
                # c.attr(cluster="true", fontcolor='black')
                # for idx, row in behave_dfs.iterrows():
                #     prob = np.round(row['AVG_BEHAVIOR_PROBABILITY'], 2)
                #     c.node(f'{row['BEHAVIOR']}', label=f"{row['BEHAVIOR']}\n{prob}", color=env, fontcolor='black',
                #            height=str(row['AVG_BEHAVIOR_PROBABILITY']), shape='circle', style='filled')

                # for idx, row in trans_dfs.iterrows():
                #     scaled = 10 * row['TRANSITION_PROBABILITY']
                #     weight = 10 * np.round(row['TRANSITION_PROBABILITY'], 2)
                #     if weight < prob_threshold:
                #         continue
                #     g.edge(f'{row['BEHAVIOR']}', f'{row['BEHAVIOR_NEXT']}',
                #         color='slategray', label=str(weight), labelloc='c',
                #         fontsize='15', penwidth=str(scaled), labelfontcolor='red')
            legend = convert_to_legend(behavior_legend_keys);
            # legend_lines = str(legend).splitlines()
            # legend_lines = legend_lines[1:-1]
            # g.body += legend_lines
            legend.render(f'{root_dir}/FightClubChains/5PercentThreshold/Legends/{fish}Behavior{env}ChainModel_Legend_{prob_threshold}Percent', quiet=True, format='jpeg', cleanup=True)
            # g.render(f'{fish}Behavior{env}ChainModel', quiet=True, format='png', cleanup=True)
            g.render(f'{root_dir}/FightClubChains/5PercentThreshold/{fish}Behavior{env}ChainModel', quiet=True, format='jpeg', cleanup=True)


def constrain_value(val: float, min_val: float, max_val: float) -> float:
    return max(min(val, max_val), min_val)

def convert_to_legend(list_of_names: list[str]) -> gv.Source:
    formatted = []
    for idx, name in enumerate(list_of_names):
        [n, prob] = name.split(' ')
        color = color_map[n] if color_map[n] is not None else color_map['DEFAULT']
        formatted.append(f'''<tr>
                <td>{' '.join(n.lower().capitalize().split('_'))}</td>
                <td>{prob}%</td>
                <td cellpadding="4">
                    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
                        <TR>
                         <TD BGCOLOR="{color}"></TD>
                        </TR>
                    </TABLE>
                </td>
            </tr>''')

    return gv.Source(f'''digraph {{
        subgraph {{
            bgcolor = "white";
            rank = sink;
            margin = 0;
            label = "";
            Legend [shape=none, margin=0, padding=0, label=<
                <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                        <tr>
                            <td><b>Behavior</b></td>
                            <td><b>Frequency</b></td>
                            <td><b>Color</b></td>
                        </tr>
                    {"\n".join(formatted)}
                </TABLE>
            >];
        }}
    }}''')