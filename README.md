# BlueYellowBehavior: Transition Matrix Generator

A Python program that creates Transition Matrices using Blue/Yellow Fish data in CSV.

----------------------------------

## Details
- Reads CSV files containing relevant fish data, and creates transition matrices based on said data
- Created transition matrices are grouped by either time, behavioral category, or left as is (basic)
    - Time grouped matrices are partitioned into multiple matrices by the hour in which each behavior occurred for the first 3 hours of the recorded data
    - Behavior category grouped matrices visually group and color behavior nodes together by the category they belong to
- Every part of a given matrix represents some aspect of the provided data
    - Behavior node sizes are set according to how often a given behavior occurred throughout the recorded data (i.e. more frequently occurring behaviors have larger nodes)
    - Transition arrow widths are set according to the ratios of a given behavior transitioning to another behavior
- Behavior node colors can be set by the user via a provided color mapping
- Capable of accepting a JSON Job Configuration file that will auto process multiple sets of data as separate job runs (see section *Using a Job Config File* of this README)
  with
- Creates Key Legends displaying which colored nodes map to each behavior
- Outputs the original Graphviz code generated to create the transition matrices

----------------------------------

## Initial Environment Set Up
1. Download and Install the latest version of [Python](https://www.python.org/downloads/)
2. Download and Install the latest version of [Graphviz](https://graphviz.org/download/)
    - Follow the download instructions according to your operating system
3. Clone this repository by running `git clone git@github.com:QCAlvaradoLab/BlueYellowBehavior.git` in your terminal/command-line, or by downloading and opening the Zip file
4. Using the terminal/command-line, navigate to the inside of this folder and run `python3 -m pip install -r requirements.txt`
    - **Optionally BEFORE running the above command, you can set up a virtual environment for separation of concerns by running the commands below in order**
        - `python3 -m venv .venv`
        - If using Windows: `.venv\Scripts\activate`
        - If using MacOS/Linux: `source .venv/bin/activate`
        - To exit this virtual environment run `deactivate` in the terminal/command-line
    - This installs the necessary python modules for running the code

----------------------------------

## Running and Editing Scripts

### Using the Code as Is
To run the code as is, simply replace the values for the `input` and `output` variables on lines 43 and 44 in `main.py` with the
file paths to the folder containing the relevant data you wish to input, and then run `python3 main.py` in your
terminal/command-line. This will create transition matrices for basic, time, and behavioral category groupings,
as well as their corresponding legends and Graphviz code and place them in the provided output folder.

&nbsp;

### Using a Job Config File
The Job Config File is in JSON format and uses the following structure
```json
{
  "jobs": [
    {
      "input_folder": "some/input/data_folder/path",
      "output_folder": "some/output/data_folder/path"
      "job_name": "Some Job Name",
      "subject": "blue | yellow",
      "environment": "blue | yellow",
      "color_map": {
        "behavior1": "hexcode or valid color name",
        "behavior2": "hexcode or valid color name",
        "behavior3": "hexcode or valid color name"
        ...
      },
      "group_by": "basic | time | behavioral category",
      "attach_legend": true | false
    },
    ...
  ]
}
```
Config Properties:
- `jobs` = a list of dictionary objects representing a given processing job to run
- `input_folder` = the relative path to the folder containing the data to be processed
- `output_folder` = the relative path to the folder to which the output matrices should be placed
- `job_name` = the name of the job to be processed
- `subject` = the subject fish of the data being process (only accepts 'blue' or 'yellow' as options)
- `environment` = the color of the environment in which the subject has been placed (only accepts 'blue' or 'yellow' as options)
- `color_map` = a dictionary object that maps all unique behaviors that occurred to a specific color (matrix nodes will appear with their mapped colors)
- `group_by` = how the matrix should be partitioned or how nodes should be grouped (only accepts 'basic', 'time', or 'behavioral category' as options)
- `attach_legend` = a boolean that indicates if the generated key legend should be attached to the graph itself rather than be a separate svg file (defaults to false)

To run the code with a config file, replace line 105 in `main.py` with `main()`. That section should now look like this:
```python
if __name__ == '__main__':
    main()
```
Then run `python3 main.py <ConfigFilePath>` where "<ConfigFilePath>" is the relative path to the config file. The program should then start processing
each job specified in the config file. For a good example of a sample job config file, see `configs/sample_job_config.json` in this repository
