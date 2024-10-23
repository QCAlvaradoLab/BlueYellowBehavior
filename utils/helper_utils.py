import os
from re import A
import string
import math
import random
import time

import pandas as pd
import graphviz as gv
import numpy as np

from utils import constants as const


class BehaviorTransitionData:
    def __init__(
        self,
        input_dir_path: str,
        output_dir_path: str,
        subject: str,
        environment: str,
        color_map: dict[str, str],
        group_by: str = 'BASIC',
        edge_visibility_threshold: float = 0.05
    ):
        raw_data = import_data_from_dir(input_dir_path)
        trans_df_formatted, behave_df_formatted = format_data(raw_data, group_by)

        self.transition_df = trans_df_formatted
        self.behavior_df = behave_df_formatted

        self.subject = subject
        self.environment = environment
        self.group_by = group_by
        self.edge_visibility_threshold = edge_visibility_threshold

        self.color_map = color_map
        self.color_map['DEFAULT'] = self.__get_color('DEFAULT')
        self.color_map['ENV_YELLOW'] = self.__get_color('ENV_YELLOW', default='#FFFFCC')
        self.color_map['ENV_BLUE'] = self.__get_color('ENV_BLUE', default='#CCFFFF')

        self.output_dir_path = output_dir_path

    def output_dfs_as_csvs(self):
        self.transition_df.to_csv(self.output_dir_path + f'/{self.group_by}/transition_df.csv', index=False)
        self.behavior_df.to_csv(self.output_dir_path + f'/{self.group_by}/behavior_df.csv', index=False)

    def create_markov_chain_graph(self, attach_legend: bool | None = None):
        graph_list: list[gv.Digraph] = [self.__init_new_digraph(add_label=True, hour=1 if self.group_by == 'TIME' else None)]
        behavior_list: list[list[tuple[str, str, str, float]]] = [[]]
        color_map_categorical = {
            'AGGRESSIVE': '#ff0000',
            'REPRODUCTIVE': '#00ff00',
            'AVERSIVE': '#0000ff'
        }
        behavior_map = {}
        sub_graphs: dict[str, gv.Digraph] = dict()
        if self.group_by == 'BEHAVIORAL_CATEGORY':
            behavior_map = map_two_columns(self.behavior_df, 'BEHAVIOR', 'BEHAVIORAL_CATEGORY')
            self.__set_color_gradients(color_map_categorical, 'BEHAVIORAL_CATEGORY', 'BEHAVIOR')

        for idx, row in self.behavior_df.iterrows():
            behavior_name = str(row['BEHAVIOR'])
            category_name = str(row[const.BEHAVIORAL_CATEGORY]) if self.group_by == const.BEHAVIORAL_CATEGORY else 'None'

            color_to_use = self.__get_color(behavior_name)

            raw_frequency = row['BEHAVIOR_PROBABILITY']
            prob = round_percent(raw_frequency)
            node_size = constrain_value(raw_frequency * 10, 0.5, 3)
            graph_idx = 0

            if self.group_by == 'BEHAVIORAL_CATEGORY':
                if sub_graphs.get(category_name) is None:
                    sub_graphs[category_name] = self.__init_new_digraph(add_label=False, cluster='true', rankdir='TB', idx=idx)
                sub_graphs[category_name].node(
                    name=f'{behavior_name}',
                    color=color_to_use,
                    label=' ', # If not provided, node name appears on node. Setting it to be a single whitespace character allows for nodes with no text
                    fontcolor='black',
                    height=str(raw_frequency),
                    shape='circle',
                    style='filled',
                    width=str(node_size)
                )

            else:
                if self.group_by == 'TIME':
                    hour = row['HOUR_PERFORMED']
                    if hour > 3:
                        continue
                    if len(graph_list) < hour:
                        graph_list.append(self.__init_new_digraph(add_label=True, hour=int(hour)))
                        behavior_list.append([])
                    graph_idx = hour - 1

                graph_list[graph_idx].node(
                    name=f'{behavior_name}',
                    color=color_to_use,
                    label=' ', # If not provided, node name appears on node. Setting it to be a single whitespace character allows for nodes with no text
                    fontcolor='black',
                    height=str(raw_frequency),
                    shape='circle',
                    style='filled',
                    width=str(node_size)
                )

            behavior_list[graph_idx].append((behavior_name, str(category_name), color_to_use, prob))

        for _, sub_graph in sub_graphs.items():
            graph_list[0].subgraph(sub_graph)

        for _, row in self.transition_df.iterrows():
            current_behavior = str(row['BEHAVIOR'])
            next_behavior = str(row['BEHAVIOR_NEXT'])

            color_to_use = self.__get_color(current_behavior)
            if self.group_by == 'BEHAVIORAL_CATEGORY':
                current_cat = behavior_map[current_behavior][0]
                next_cat = behavior_map[next_behavior][0]
                same_category = current_cat == next_cat
                color_to_use = color_map_categorical[current_cat] if same_category else 'black'

            raw_frequency = row['TRANSITION_PROBABILITY']
            weight = round_percent(raw_frequency)

            graph_idx = 0
            if self.group_by == 'TIME':
                hour = row['HOUR_PERFORMED']
                if hour > 3:
                    continue
                graph_idx = hour - 1

            if weight < self.edge_visibility_threshold * 100:
                continue

            edge_width = str(constrain_value(raw_frequency * 20, 0.5, 7))
            graph_list[graph_idx].edge(
                tail_name=current_behavior,
                head_name=next_behavior,
                color=color_to_use,
                penwidth=edge_width,
            )

        output_dir = f'{self.output_dir_path}/{self.group_by}'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for idx, g in enumerate(graph_list):
            file_name = f'{self.subject}FishBehavior{self.environment}ChainModel'
            file_name += f'Hour{idx+1}' if self.group_by == 'TIME' else ''

            if attach_legend is not None:
                legend = self.__create_graph_legend(behavior_list[idx], show_category=self.group_by == 'BEHAVIORAL_CATEGORY')
                if attach_legend is True:
                    legend_lines = str(legend).splitlines()
                    legend_lines = legend_lines[1:-1]
                    g.body += legend_lines
                    g.unflatten(stagger=3)
                else:
                    if not os.path.exists(f'{output_dir}/Legends'):
                        os.makedirs(f'{output_dir}/Legends')
                    legend.render(
                        filename=f'{output_dir}/Legends/{file_name}_Legend',
                        quiet=True,
                        format='jpeg',
                        cleanup=True
                    )
            g.save(f'{output_dir}/source_code.gv')
            g.render(
                filename=f'{output_dir}/{file_name}',
                quiet=True,
                format='jpeg',
                cleanup=True
            )


    def __create_graph_legend(self, behavior_list: list[tuple[str, str, str, float]], show_freqency: bool = True, show_category: bool = False) -> gv.Source:
        formatted = []
        for idx, (behavior, category, color_to_use, freqency) in enumerate(behavior_list):
            # color = self.color_map.get(behavior) if self.color_map.get(behavior) is not None else self.color_map['DEFAULT']
            formatted_behavior = behavior.lower().capitalize().split("_")
            if formatted_behavior[-1] == '\\u2640': # weird formatting issue that needs to be fixed manually here
                formatted_behavior[-1] = str('\u2640')
            elif formatted_behavior[-1] == '\\u2642':
                formatted_behavior[-1] = str('\u2642')
            formatted.append(f'''<tr>
                <td>{" ".join(formatted_behavior)}</td>
                    {f"<td>{freqency}%</td>" if show_freqency is True else ""}
                    {f"<td>{category}</td>" if show_category is True else ""}
                    <td cellpadding="4">
                        <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
                            <TR>
                                <TD BGCOLOR="{color_to_use}"></TD>
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
                                {f"<td><b>Frequency</b></td>" if show_freqency is True else ""}
                                {f"<td><b>Category</b></td>" if show_category is True else ""}
                                <td><b>Color</b></td>
                            </tr>
                        {"\n".join(formatted)}
                    </TABLE>
                >];
            }}
        }}''')


    def __get_color(self, key: str, default: str = 'antiquewhite') -> str:
        return self.color_map[key] if self.color_map.get(key) is not None else default

    def __set_colors_by_list(self, values: list[str], colors: list[str]):
        if len(values) != len(colors):
            raise Exception('bruh the list args are different lengths')
        for idx in range(len(values)):
            self.color_map[values[idx]] = colors[idx]

    def __set_color_gradients(self, base_color_map: dict[str, str], color_column_get: str, color_column_set: str):
        col_map = map_two_columns(self.behavior_df, color_column_get, color_column_set)
        for key, val_list in col_map.items():
            color = base_color_map.get(key)
            if color is not None:
                color_hex = color_to_num(color)
                gradient = make_color_gradient(color_hex, len(val_list))
                self.__set_colors_by_list(val_list, gradient)


    def __init_new_digraph(self, add_label: bool, cluster: str = 'true', rankdir: str = 'LR', idx: int | None = None, hour: float | None = None) -> gv.Digraph:
        graph_title = f'{self.subject} Fish Behaviors{f' {idx}' if idx is not None else ''}'
        if len(self.environment) > 0:
            graph_title += f' in {self.environment} Environment'
        if hour is not None:
            graph_title += f' (Hour {hour})'

        g = gv.Digraph(graph_title)
        label = f'{graph_title}: Transition Probability >{self.edge_visibility_threshold * 100}%'
        bgcolor = self.subject.upper() if self.group_by == 'BEHAVIORAL_CATEGORY' else self.environment.upper()
        bgcolor = self.__get_color(f'ENV_{bgcolor}')
        g.attr(
            fixed_size='false',
            overlap='scale',
            size='50',
            bgcolor=bgcolor,
            fontcolor='black',
            packMode='clust',
            compound='true',
            label=(label if add_label is True else ""),
            fontname='fira-code',
            labelloc='t',
            rank='source' if rankdir == 'TB' else None,
            rankdir=rankdir,
            cluster=cluster,
            peripheries='0'
        )
        return g


def import_data_from_dir(dir_path: str, column_names: list[str] = []) -> dict[str, pd.DataFrame]:
    df: dict[str, pd.DataFrame] = {}
    filenames = [filename for filename in os.listdir(dir_path) if filename.endswith('.csv') or filename.endswith('.tsv')]
    for filename in filenames:
        name, ext = filename.split('.')
        if ext == 'csv':
            temp_df = pd.read_csv(os.path.join(dir_path, filename))
            df[name] = pd.DataFrame(temp_df[column_names]) if len(column_names) else temp_df.copy()
        elif ext == 'tsv':
            temp_df = pd.read_csv(os.path.join(dir_path, filename), sep='\t')
            df[name] = pd.DataFrame(temp_df[column_names]) if len(column_names) else temp_df.copy()

    return df


def format_data(df_map: dict[str, pd.DataFrame], group_by: str = '') -> tuple[pd.DataFrame, pd.DataFrame]:
    transitions = {}
    behaviors = {}
    for idx, (name, sub_df) in enumerate(df_map.items()):
        sub_transition = pd.DataFrame()
        sub_behavior = pd.DataFrame()

        sub_transition[const.BEHAVIOR] = sub_df['Behavior'].map(lambda x: upper_snake(str(x)))
        if group_by == const.BEHAVIORAL_CATEGORY:
            sub_transition[const.BEHAVIORAL_CATEGORY] = sub_df['Behavioral category'].map(lambda x: upper_snake(str(x)))

        t_idx_label = sub_transition[sub_transition['BEHAVIOR'] == 'OUT_OF_VIEW'].index
        # You can ignore the generated warning below. The above variable works fine as an argument
        sub_transition.drop(t_idx_label, inplace=True)

        sub_behavior['BEHAVIOR'] = sub_transition['BEHAVIOR'].copy()
        if group_by == const.BEHAVIORAL_CATEGORY:
            sub_behavior[const.BEHAVIORAL_CATEGORY] = sub_transition[const.BEHAVIORAL_CATEGORY].copy()

        sub_transition['BEHAVIOR_NEXT'] = sub_transition['BEHAVIOR'].shift(-1)

        # comment line below when we figure out minutes to seconds conversions
        if sub_df.get('frame') is not None:
            sub_df['Time'] = sub_df['Time'].map(lambda _: 1)
        time_next = sub_df['Time'].shift(-1)
        sub_transition['BEHAVIOR_DURATION'] = time_next - sub_df['Time']
        sub_behavior['BEHAVIOR_DURATION'] = time_next = sub_df['Time']

        if group_by == 'TIME':
            sub_behavior['HOUR_PERFORMED'] = sub_df['Time'].transform(lambda x: math.ceil(x / 3600))
            sub_transition['HOUR_PERFORMED'] = sub_df['Time'].transform(lambda x: math.ceil(x / 3600))

            transitions[name] = sub_transition.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT', 'HOUR_PERFORMED']).count()
            behaviors[name] = sub_behavior.groupby(['BEHAVIOR', 'HOUR_PERFORMED']).count()
        elif group_by == 'BEHAVIORAL_CATEGORY':
            transitions[name] = sub_transition.groupby([const.BEHAVIOR, const.BEHAVIOR_NEXT, const.BEHAVIORAL_CATEGORY]).count()
            behaviors[name] = sub_behavior.groupby([const.BEHAVIOR, const.BEHAVIORAL_CATEGORY]).count()
        else:
            transitions[name] = sub_transition.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT']).count()
            behaviors[name] = sub_behavior.groupby(['BEHAVIOR']).count()

        transitions[name].rename(columns={ 'BEHAVIOR_DURATION': 'TRANSITION_COUNTS' }, inplace=True)
        behaviors[name].rename(columns={ 'BEHAVIOR_DURATION': 'BEHAVIOR_COUNTS' }, inplace=True)

    transition_dataframe = pd.concat(transitions.values(), sort=False)
    transition_dataframe.fillna(0, inplace=True)

    behavior_dataframe = pd.concat(behaviors.values(), sort=False)
    behavior_dataframe.fillna(0, inplace=True)

    if group_by == const.TIME:
        transition_dataframe = pd.DataFrame(transition_dataframe.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT', 'HOUR_PERFORMED']).sum())
        transition_dataframe.reset_index(level=[0, 1, 2], inplace=True)

        behavior_dataframe = pd.DataFrame(behavior_dataframe.groupby(['BEHAVIOR', 'HOUR_PERFORMED']).sum())
        behavior_dataframe.reset_index(level=[0, 1], inplace=True)

        transition_dataframe['BEHAVIOR_TOTALS'] = transition_dataframe.groupby(['BEHAVIOR', 'HOUR_PERFORMED'])[['TRANSITION_COUNTS']].transform('sum')
        transition_dataframe['TRANSITION_PROBABILITY'] = transition_dataframe['TRANSITION_COUNTS'] / transition_dataframe['BEHAVIOR_TOTALS']

        behavior_dataframe['BEHAVIOR_TOTALS_BY_HOUR'] = behavior_dataframe.groupby(['HOUR_PERFORMED'])[['BEHAVIOR_COUNTS']].transform('sum')
        behavior_dataframe['BEHAVIOR_PROBABILITY'] = behavior_dataframe['BEHAVIOR_COUNTS'] / behavior_dataframe['BEHAVIOR_TOTALS_BY_HOUR']
    elif group_by == const.BEHAVIORAL_CATEGORY:
        transition_dataframe = pd.DataFrame(transition_dataframe.groupby([const.BEHAVIOR, const.BEHAVIOR_NEXT, const.BEHAVIORAL_CATEGORY]).sum())
        transition_dataframe.reset_index(level=[0, 1, 2], inplace=True)

        behavior_dataframe = pd.DataFrame(behavior_dataframe.groupby([const.BEHAVIOR, const.BEHAVIORAL_CATEGORY]).sum())
        behavior_dataframe.reset_index(level=[0, 1], inplace=True)

        transition_dataframe['BEHAVIOR_TOTALS'] = transition_dataframe.groupby([const.BEHAVIOR, const.BEHAVIORAL_CATEGORY])[['TRANSITION_COUNTS']].transform('sum')
        transition_dataframe['TRANSITION_PROBABILITY'] = transition_dataframe['TRANSITION_COUNTS'] / transition_dataframe['BEHAVIOR_TOTALS']

        behavior_dataframe['BEHAVIOR_PROBABILITY'] = behavior_dataframe['BEHAVIOR_COUNTS'] / behavior_dataframe['BEHAVIOR_COUNTS'].sum()
    else:
        transition_dataframe = pd.DataFrame(transition_dataframe.groupby(['BEHAVIOR', 'BEHAVIOR_NEXT']).sum())
        transition_dataframe.reset_index(level=[0, 1], inplace=True)

        behavior_dataframe = pd.DataFrame(behavior_dataframe.groupby(['BEHAVIOR']).sum())
        behavior_dataframe.reset_index(level=[0], inplace=True)

        transition_dataframe['BEHAVIOR_TOTALS'] = transition_dataframe.groupby(['BEHAVIOR'])[['TRANSITION_COUNTS']].transform('sum')
        transition_dataframe['TRANSITION_PROBABILITY'] = transition_dataframe['TRANSITION_COUNTS'] / transition_dataframe['BEHAVIOR_TOTALS']

        behavior_dataframe['BEHAVIOR_PROBABILITY'] = behavior_dataframe['BEHAVIOR_COUNTS'] / behavior_dataframe['BEHAVIOR_COUNTS'].sum()

    return (transition_dataframe, behavior_dataframe)



def constrain_value(val: float, min_val: float, max_val: float) -> float:
    return max(min(val, max_val), min_val)


# Untyped args to avoid unhelpful type errors from PyRight
def round_percent(val, sig_figures = 1) -> float:
    return np.round(val * 100, sig_figures)


# All color hexcode inputs should be in the format '#XXXXXX' where 'X' is a valid hexadecimal character
# The color hexcode is case agnostic
# Examples: #000000, #ffffff, #2Ab3eD
def is_valid_color_hex(hex: str) -> bool:
    return all([
        hex.startswith('#'),
        len(hex) == 7,
        all(c in string.hexdigits for c in hex[1:]),
    ])

# Color functions
def random_hex_char() -> str:
    return hex(random.randrange(0, 16))
def random_color_hex(seed: int | None = None) -> str:
    if seed is not None:
        random.seed(seed)
    return num_to_color(random.randrange(0, const.MAX_HEX_VALUE + 1))
def num_to_color(val: int) -> str:
    return '#' + (hex(val)[2:]).rjust(6, '0') # Slice off the '0x' from the front so we can pad with 0's if needed
def color_to_num(val: str) -> int:
    return int('0x' + val[1:], 16)
def make_color_gradient(base_hex: int, partitions: int) -> list[str]:
    gradient: list[str] = []
    increment = math.ceil(const.MAX_HEX_VALUE / (partitions + 1))
    for i in range(increment, const.MAX_HEX_VALUE, increment):
        gradient.append(num_to_color(base_hex | i))
    return gradient

# Used for standardizing user input data to prevent reference errors
# Checks for specific keys to ensure important parameters are present (i.e. jobs, input/output folders, etc)
def format_json_input(d: dict) -> dict[str, str | list[object]]:
    result = { key.upper(): val for (key, val) in d.items() }
    for idx, job in enumerate(result[const.JOBS]):
        formatted_job = { key.upper(): val for (key, val) in job.items() }
        if formatted_job.get(const.INPUT_FOLDER) is None:
            formatted_job[const.INPUT_FOLDER] = result.get(const.GLOBAL_INPUT_FOLDER)

        if formatted_job.get(const.OUTPUT_FOLDER) is None:
            formatted_job[const.OUTPUT_FOLDER] = result.get(const.GLOBAL_OUTPUT_FOLDER)

        if formatted_job.get(const.ATTACH_LEGEND) is None:
            formatted_job[const.ATTACH_LEGEND] = result.get(const.GLOBAL_ATTACH_LEGEND)


        formatted_job[const.COLOR_MAP] = { upper_snake(key): val for (key, val) in formatted_job.get(const.COLOR_MAP).items() }
        formatted_job[const.GROUP_BY] = upper_snake(formatted_job.get(const.GROUP_BY))

        result[const.JOBS][idx] = formatted_job

    return result

# Formats strings from 'xxxx xxxx xxxx' to 'XXXX_XXXX_XXXX'
def upper_snake(s: str) -> str:
    return '_'.join(str(s).upper().split(' '))

# Formats strings from 'XXXX_XXXX_XXXX' to 'Xxxx xxxx xxxx'
def split_to_spaced(s: str) -> str:
    return ' '.join(str(s).lower().capitalize().split('_'))

def map_two_columns(df: pd.DataFrame, keys_col: str, values_col: str) -> dict[str, list[str]]:
    results = dict()
    df_dict = df.to_dict('records')

    for record in df_dict:
        if results.get(record[keys_col]) == None:
            results[record[keys_col]] = []
        results[record[keys_col]].append(record[values_col])

    return results

def hms_to_seconds(time_str: str, no_hours: bool = False) -> float:
    mapped_over = list(map(float, time_str.split(':')))
    while (len(mapped_over) < 3):
        mapped_over.insert(0, 0)
    h, m, s = mapped_over

    return h * 3600 + m * 60 + s