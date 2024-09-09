import sys
import getopt

from mc_utils import *

import math
import itertools


# Script usage: python3 markov_chains.py -i <InputFile> -p <TransitionProbabilityMinimum (Value between 0 and 1 exclusive)>
def main(argv):
  input_file = None
  transition_probability_minimum = -1

  try:
    opts, _ = getopt.getopt(argv, 'i:p:')
    for opt, arg in opts:
      if opt == '-i':
        input_file = arg
      elif opt == '-p':
        transition_probability_minimum = float(arg)
      else:
        raise Exception(f'Error: invalid flag detected: Flag = {opt}')
    if input_file == None:
      raise Exception('Error: Input file name was not provided')
  except getopt.GetoptError:
    print('Error: problem parsing arguments')
    sys.exit(2)

  reformatted_data = santize_input(input_file)
  for _, data in reformatted_data.items():
    generate_markov_chains(data, transition_probability_minimum)



if __name__ == '__main__':
  main(sys.argv[1:])