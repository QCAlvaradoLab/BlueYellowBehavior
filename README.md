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
  - 

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