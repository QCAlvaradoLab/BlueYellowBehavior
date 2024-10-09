from typing import Final

# Config Param name constants
GLOBAL_INPUT_FOLDER: Final[str] = 'GLOBAL_INPUT_FOLDER'
GLOBAL_OUTPUT_FOLDER: Final[str] = 'GLOBAL_OUTPUT_FOLDER'
GLOBAL_ATTACH_LEGEND: Final[str] = 'GLOBAL_ATTACH_LEGEND'
PARENT_OUTPUT_FOLDER: Final[str] = 'PARENT_OUTPUT_FOLDER'
JOBS: Final[str] = 'JOBS'
# JOBS sub param names
JOB_NAME: Final[str] = 'JOB_NAME'
INPUT_FOLDER: Final[str] = 'INPUT_FOLDER'
OUTPUT_FOLDER: Final[str] = 'OUTPUT_FOLDER'
SUBJECT: Final[str] = 'SUBJECT'
ENV: Final[str] = 'ENV'
COLOR_MAP: Final[str] = 'COLOR_MAP'
GROUP_BY: Final[str] = 'GROUP_BY'
ATTACH_LEGEND: Final[str] = 'ATTACH_LEGEND'

# Data input column names/group by options
BASIC: Final[str] = 'BASIC'
BEHAVIOR: Final[str] = 'BEHAVIOR'
BEHAVIOR_NEXT: Final[str] = 'BEHAVIOR_NEXT'
TIME: Final[str] = 'TIME'
BEHAVIORAL_CATEGORY: Final[str] = 'BEHAVIORAL_CATEGORY'
STATUS: Final[str] = 'STATUS' # this one is currently not in use

# Hex Color codes for making color gradients
MAX_HEX_VALUE: Final[int] = 0xFFFFFF
WHITE_FULL: Final[str] = '#FFFFFF'
WHITE_90: Final[str] = '#CCCCCC'
WHITE_75: Final[str] = '#AAAAAA'
WHITE_50: Final[str] = '#777777'
WHITE_25: Final[str] = '#444444'