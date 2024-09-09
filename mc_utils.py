# import util packages
import csv
from dataclasses import dataclass, asdict
import itertools
import math
# import science packages
import numpy as np
import pandas as pd
# import plotting/graphing packages
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx


# user defined types for readability
type BehaviorWithTimestamp = tuple[str, float]
type SubjectBehaviorLists = dict[str, list[BehaviorWithTimestamp]]

class MarkovChainFunctionInput:
  def __init__(self, path_to_csv: str, video_id: float):
    self.path_to_csv: str = path_to_csv
    self.output_file: str = f'Markov_Chains_VideoID-{video_id}'
    self.video_id: float = video_id
    self.all_unique_behaviors: set = set()
    self.subject_behaviors: SubjectBehaviorLists = {}

  def __str__(self):
    return f'''
      CSV File: {self.path_to_csv}
      Output File: {self.output_file}
      Video ID: {self.video_id}
      All Unique Behaviors: [{','.join(self.all_unique_behaviors)}]
      Subject Behavior List: {[f'{key}: {self.subject_behaviors[key]}\n' for key in self.subject_behaviors]}
    '''

  def update_subject_behaviors(self, subject: str, bts: BehaviorWithTimestamp):
    self.all_unique_behaviors.add(bts[0])
    if subject not in self.subject_behaviors:
      self.subject_behaviors[subject] = []

    self.subject_behaviors[subject].append(bts)

  def print_unique_behaviors(self):
    print(self.all_unique_behaviors)


# Sanitizes and formats csv input file into easily digestible dictionary for later use
def santize_input(path_to_csv: str) -> dict[float, MarkovChainFunctionInput]:
  final_output: dict[float, MarkovChainFunctionInput] = {}

  with open(path_to_csv, 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    header_row = next(csv_reader)
    header_row = [var.strip().upper() for var in header_row]

    behavior_idx = -1
    subject_idx = -1
    timestamp_idx = -1
    video_id_idx = -1

    if 'BEHAVIOR' in header_row:
      behavior_idx = header_row.index('BEHAVIOR')
    else:
      raise Exception('Error: missing "Behavior" column')

    if 'SUBJECT' in header_row:
      subject_idx = header_row.index('SUBJECT')
    else:
      raise Exception('Error: missing "Subject" column')

    if 'TIME' in header_row:
      timestamp_idx = header_row.index('TIME')
    else:
      raise Exception('Error: missing "Time" column')

    if 'ID' in header_row:
      video_id_idx = header_row.index('ID')
    else:
      raise Exception('Error: missing "Id" column')

    for row in csv_reader:
      behavior_value = row[behavior_idx].strip()
      subject_value = row[subject_idx].strip()
      timestamp_value = float(row[timestamp_idx].strip())
      video_id_value = float(row[video_id_idx].strip())

      if behavior_value.find('/') > -1:
        multiple_valid_behaviors = behavior_value.split('/')
        multiple_valid_behaviors = [var.strip() for var in multiple_valid_behaviors]
        behavior_value = '/'.join(multiple_valid_behaviors)

      behavior_value = behavior_value.replace(' ', '-').upper()

      if video_id_value not in final_output:
        final_output[video_id_value] = MarkovChainFunctionInput(path_to_csv, video_id_value)

      final_output[video_id_value].update_subject_behaviors(subject_value, (behavior_value, timestamp_value))

  return final_output



# default value assigned to numeric variables to prevent divide by 0 errors
epsilon = 1e-10
# matplotlib figure parameters
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams.update({'font.size': 14})

# Generates markov chains based on the provided input
def generate_markov_chains(
  data: MarkovChainFunctionInput,
  tp_min: float = -1
):
  behavior_perms = list(itertools.permutations(data.all_unique_behaviors, 2))
  behavior_perms = ['|'.join(perm) for perm in behavior_perms]

  behavior_perms.extend([f'{behavior}|{behavior}' for behavior in data.all_unique_behaviors])
  behavior_perms.extend(data.all_unique_behaviors)

  behavior_transition_counts = {}
  behavior_pair_names_for_total = []

  nx.DiGraph()

  for subject in data.subject_behaviors:
    if subject not in behavior_transition_counts:
      behavior_transition_counts[subject] = { perm: 0 for perm in behavior_perms if '|' in perm }

    behaviors = data.subject_behaviors[subject]
    for idx in range(len(behaviors) - 1):
      first_behavior, _ = behaviors[idx]
      second_behavior, _ = behaviors[idx + 1]
      behavior_pair = '|'.join([first_behavior, second_behavior])