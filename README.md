# MarkovChainGeneratorScripts
Python Scripts for generating markov chain plots/graphs

Project Details:
- Step 1:
  - Markov chains for each fish color and environment color permutations (4 chains as of now, 1 graph)
  - Averaging the 6 replicates for each behavior to occur
- Step 2:
  - Markov chains for each environment showing blue and yellow fish behavior (2 chains as of now, 1 graph)
- Step 3:
  - Divide up Markov chains from step 1 into behavior for each hour (3 hours total)

Project Requirements:
- Be able to run script with minimal input
  - Should only need to specify CSV file as argument
  - Config file an option?
- Script should be able to work with agnostic data
  - Should handle multiple different types of behaviors between different data sets
  - Columns are consistent between datasets?
- Script should be easily readable and editable if necessary by a lab tech/researcher with minimal coding knowledge
  - Good documentation
  - Requested changes should be achievable with minimal edits by lab tech/researcher
- Result should output clean Markov Chain graphs
  - Clear node and arrow labeling
  - Behaviors' colors grouped by category?


Project Questions:
- Do different video ID's imply different fish recorded?
  - Differentiate between different videos?
- How many fish are involved in the dataset (currently assuming 2 fish)?
- What is the Status column?
- Differentiate between Dominant and Subordinate behaviors
  - Should Markov Chain separate Dominant's behaviors from Subordinate behaviors into their own graphs? (I assume no)
  - How to handle doubled up actions (i.e. two Subordinate's behaviors followed up by the Dominant's behavior)?


Tasks for next week:
- Darker colors for nodes in past graphs (hourly and regular for all fish combos)
- Andrew's graphs with white background and darker colors + fix weird red colors
- Readme for this
- add bullet point details to the paper

- main libraries used as seen in requirements.txt file:
  - graphviz: v0.20.3
  - pandas: v2.2.3
- libraries used as dependencies for graphviz and pandas (probably unnecessary to include since I don't actually import them, but here they are anyway):
  - numpy: v2.1.2
  - python-dateutil: v2.9.0.post0
  - pytz: v2024.2
  - six: v1.16.0
  - tzdata: v2024.2
- implementation:
  - loaded each folder of csv files containing relevant data into pandas dataframes for formatting/organization
    - csv files represented different filming sessions of the same subject
  - data was cleaned and organized to prevent discrepency errors
  - data was aggregated into the following pandas dataframe schemas (schema changes depending on analysis type i.e. time, category, and/or as is):
    - Behavior Dataframe: contains aggregated totals of all observed behaviors
      - Columns available to all analysis types:
        - BEHAVIOR: the behavior exhibited by the subject
        - BEHAVIOR_COUNTS: the total count of a given behavior observed across all of the provided data
        - BEHAVIOR_PROBABILITY: the percentage of how often a behavior was performed over the total count of all behaviors performed on a scale between 0 and 1
          - if analyzing based on time/hourly performance, probabilities are split across different hours recorded
      - Columns unique to time analysis:
        - HOUR_PERFORMED: the hour in which a behavior was performed
        - BEHAVIOR_TOTALS_BY_HOUR: the total count of a given behavior observed within a given hour in the recording
      - Columns unique to category analysis:
        - BEHAVIORAL_CATEGORY: the category in which a behavior falls under
    - Transition Dataframe: contains aggregated totals for the different behavior transitions observed
      - Columns available to all analysis types:
        - BEHAVIOR: the behavior exhibited by the subject
        - BEHAVIOR_NEXT: the following behavior (created for ease of access when creating the transitions)
        - TRANSITION_COUNTS: the total count of transitions between a given behavior (BEHAVIOR) and another behavior (BEHAVIOR_NEXT) observed across all of the provided data
        - BEHAVIOR_TOTALS: the total count of a given behavior amongst all of its possible transitions
          - if analyzing based on time/hourly performance, the totals are split across different hours recorded
        - TRANSITION_PROBABILITY: the percentage of how often a specific transition from one behavior to the next was observed over the total count of all transitions from a given behavior observed on a scale between 0 and 1
          - if analyzing based on time/hourly performance, probabilities are split across different hours recorded
      - Columns unique to time analysis:
        - HOUR_PERFORMED: the hour in which a transition was observed
      - Columns unique to category analysis:
        - BEHAVIORAL_CATEGORY: the category in which a behavior (from the BEHAVIOR column) falls under
  - made multiple markov chains using the Digraph function from the graphviz library
    - graph nodes representing each behavior generated using data from Behavior Dataframe
      - node sizes based on total occurrences across all behaviors
        - smaller = occurred less, larger = occurred more
        - node sizes were clamped to specific values to prevent generated nodes from being too big or too small
      - node positions determined by graphviz "dot" graphics engine to create optimal placements
      - node colors chosen arbitrarily unless grouping by category
        - if grouped by category, node colors become gradient based on a color assigned to the given category
          - nodes for aggressive behaviors were a shade of red
          - nodes for reproductive behaviors were a shade of green
          - nodes for aversive behaviors were a shade of blue
    - directed graph connections representing behavior transitions generated using data from Transition Dataframe
      - connection widths based on total occurrences across all transitions from a given behavior
        - smaller = occurred less, larger = occurred more
        - connection widths were clamped to specific values to prevent generated connections from being too wide or too thin
      - connection colors based on the node it comes from unless grouping by category
        - for example: a directed connection from a purple node to a pink node will be purple in color
        - if grouped by category, connection colors are based on color assigned to a given category
          - connections between aggressive behavior nodes are red
          - connections between reproductive behavior nodes are green
          - connections between aversive behavior nodes are blue
          - connections between behavior nodes of different categories are black
    - additional legend created for each chain showing corresponding behavior colors and how often the behavior occurred
  - markov chain graphs exported as separate jpeg files based on subject, environment, and analysis type
    - 4 base analysis graphs
      - blue subject - blue env
      - blue subject - yellow env
      - yellow subject - blue env
      - yellow subject - yellow env
    - 12 time analysis graphs
      - graphs were separated by hour, ignoring any behaviors happening past the 4th hour
      - same as base analysis but each one split into 3 graphs
    - 2 category analysis graphs
      - environment argument unnecessary
      - blue subject
      - yellow subject
  - currently graphs generated use hard coded file inputs, but ideally would be updated to handle custom user input