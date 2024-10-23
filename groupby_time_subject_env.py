import os
from graphviz.graphs import Digraph
import pandas as pd
import graphviz as gv
import numpy as np

import math

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
            df[ft][ec] = format_data_by_hour(df_map)

    return df

def format_data_by_hour(df_map: FNameToDFrameDict) -> tuple[pd.DataFrame, pd.DataFrame]:
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

        sub_behavior['HOUR_PERFORMED'] = sub_df['Time'].transform(lambda x: math.ceil(x / 3600))
        sub_transition['HOUR_PERFORMED'] = sub_df['Time'].transform(lambda x: math.ceil(x / 3600))

        transition_dict[name] = sub_transition.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT', 'HOUR_PERFORMED']).count()
        transition_dict[name].rename(columns={ 'BEHAVIOR_DURATION': 'TRANSITION_COUNTS' }, inplace=True)

        behavior_dict[name] = sub_behavior.groupby(['BEHAVIOR', 'HOUR_PERFORMED']).count()
        behavior_dict[name].rename(columns={ 'BEHAVIOR_DURATION': 'BEHAVIOR_COUNTS' }, inplace=True)


    transition_df = pd.concat(transition_dict.values(), sort=False)
    transition_df.fillna(0, inplace=True)
    transition_df = pd.DataFrame(transition_df.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT', 'HOUR_PERFORMED']).sum())
    transition_df.reset_index(level=[0, 1, 2], inplace=True)

    transition_df['BEHAVIOR_TOTALS'] = transition_df.groupby(['BEHAVIOR', 'HOUR_PERFORMED'])[['TRANSITION_COUNTS']].transform('sum')
    transition_df['TRANSITION_PROBABILITY'] = transition_df['TRANSITION_COUNTS'] / transition_df['BEHAVIOR_TOTALS']


    behavior_df = pd.concat(behavior_dict.values(), sort=False)
    behavior_df.fillna(0, inplace=True)
    behavior_df = pd.DataFrame(behavior_df.groupby(['BEHAVIOR', 'HOUR_PERFORMED']).sum())
    # print(behavior_df['BEHAVIOR_COUNTS'])
    behavior_df.reset_index(level=[0, 1], inplace=True)

    behavior_df['BEHAVIOR_TOTALS_BY_HOUR'] = behavior_df.groupby(['HOUR_PERFORMED'])[['BEHAVIOR_COUNTS']].transform('sum')
    behavior_df['BEHAVIOR_PROBABILITY_BY_HOUR'] = behavior_df['BEHAVIOR_COUNTS'] / behavior_df['BEHAVIOR_TOTALS_BY_HOUR']
    # print(behavior_df['BEHAVIOR_PROBABILITY_BY_HOUR'])

    return (transition_df, behavior_df)


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
def init_dg(fish, env, hour, prob_threshold) -> gv.Digraph:
    g = gv.Digraph(f'{fish} Fish Behaviors in {env} Colored Environment: Hour {hour}', engine='dot')
    bgcolor = '#FFFFCC' if env == 'Yellow' else '#CCFFFF'
    g.attr(
        fixed_size='true',
        overlap='scale',
        size='50',
        # size='5,2!',
        # ratio='fill',
        # dpi='300',
        bgcolor=bgcolor, fontcolor='black',
        packMode='graph', compound='true', label=f'{fish} Fish in {env} Env (Hour {hour}): Transition Probability >{prob_threshold * 100}%',
        fontname='fira-code', labelloc='t', rankdir='LR', cluster="true")
    return g


def constrain_value(val: float, min_val: float, max_val: float) -> float:
    return max(min(val, max_val), min_val)

def markov_chains_by_hour(root_dir: str, prob_threshold = 0.05):
    fish_dfs = get_fish_dfs(root_dir, ['Blue', 'Yellow'], ['Blue', 'Yellow'])

    for (fish, env_dfs) in fish_dfs.items():
        for (env, (trans_dfs, behave_dfs)) in env_dfs.items():
            graph_list: list[gv.Digraph] = []
            # legend_list: list[gv.Digraph] = []
            behavior_legend_keys: list[list[str]] = []
            for idx, row in behave_dfs.iterrows():
                behavior_name = str(row['BEHAVIOR'])
                color_to_use = color_map[behavior_name] if color_map[behavior_name] is not None else color_map['DEFAULT']
                prob = np.round(row['BEHAVIOR_PROBABILITY_BY_HOUR'] * 100, 1)

                hour = row['HOUR_PERFORMED']
                if hour > 3:
                    continue
                if len(graph_list) < hour:
                    graph_list.append(init_dg(fish, env, hour, prob_threshold))
                    behavior_legend_keys.append([])

                behavior_legend_keys[hour - 1].append(f"{behavior_name} {prob}")

                node_size = constrain_value(row['BEHAVIOR_PROBABILITY_BY_HOUR'] * 10, 0.5, 3)
                graph_list[hour - 1].node(f'{behavior_name}', color=color_to_use,
                    # label=f"{behavior_name}\n{prob}%",
                    # label=f"{prob}%",
                    label=' ',
                    fontcolor='black', height=str(row['BEHAVIOR_PROBABILITY_BY_HOUR']), shape='circle',
                    style='filled', width=f"{node_size}")



            for idx, row in trans_dfs.iterrows():
                behavior_name = str(row['BEHAVIOR'])
                # scaled = max(min(20 * row['TRANSITION_PROBABILITY'], 10), 1)
                scaled = constrain_value(20*row['TRANSITION_PROBABILITY'], 1, 10)
                weight = np.round(row['TRANSITION_PROBABILITY'] * 100, 1)
                color_to_use = color_map[behavior_name] if color_map[behavior_name] is not None else color_map['DEFAULT']

                hour = row['HOUR_PERFORMED']
                if hour > 3:
                    continue
                if weight < prob_threshold * 100:
                    continue

                graph_list[hour - 1].edge(f'{behavior_name}', f'{row['BEHAVIOR_NEXT']}',
                    color=color_to_use, #label=f'{str(weight)}%', labelloc='c',
                    # fontsize='15',
                    penwidth=str(scaled), fontcolor='white')

            # behavior_legend_keys = [l.sort() for l in behavior_legend_keys]
            for idx, g in enumerate(graph_list):
                # body = convert_to_legend(behavior_legend_keys[idx]).pipe(encoding='utf-8')
                legend = convert_to_legend(behavior_legend_keys[idx])
                # legend_lines = str(legend).splitlines()
                # legend_lines = legend_lines[1:-1]
                # g.body += legend_lines
                # print(legend_lines)
                # legend_lines.pop(0)
                # legend_lines.pop(-1)
                # print(legend_lines)
                # g.body.insert(0, 'subgraph {')
                # g.body.append('}\n')
                # g.body = ['subgraph {', 'rank="same";'] + g.body + ['}\n']
                # print(body)
                # print([g for (_, g) in enumerate(g.__iter__())])
                # graph_legend = gv.Digraph('Legend', engine='dot')
                # graph_legend.attr(
                #     rank='sink',
                #     fontsize='10',
                #     label=f'<{convert_to_legend(behavior_legend_keys[idx])}>',
                #     size='100',
                #     shape='none',
                #     bgcolor='white'
                # )
                # with g.subgraph(graph_legend) as c:
                #     c.attr(
                #         rankdir='sink',
                #         fontsize='10',
                #         label=f'<{convert_to_legend(behavior_legend_keys[idx])}>',
                #         size='100',
                #         shape='none',
                #         bgcolor='white',
                #         fontcolor='black'
                #     )
                #     print(c.body)
                # g.subgraph(graph=f'''Legend [
                #     labelloc=b labeljust=l label=<{convert_to_legend(behavior_legend_keys)}>
                # ]''')
                # legend = gv.Digraph(body=body)
                # g.subgraph(legend)
                # g.unflatten(stagger=3)
                legend.render(f'{root_dir}/FightClubChainsByHour/5PercentThreshold/Legends/{fish}Behavior{env}ChainModel_Hour{idx+1}_Legend', quiet=True, format='jpeg', cleanup=True)
                g.render(f'{root_dir}/FightClubChainsByHour/5PercentThreshold/{fish}Behavior{env}ChainModel_Hour{idx+1}', quiet=True, format='jpeg', cleanup=True)

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
