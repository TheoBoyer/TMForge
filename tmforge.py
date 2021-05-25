"""

    Entry point for TMForge

"""

import argparse
import os
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TMForge environment for reinforcement learning')
    modes = ['run_algorithm', 'test_experiment', 'test_binding']
    parser.add_argument(
        'mode',
        choices=modes,
        help='Mode to run TMForge with. Must be one of ' + str(modes)
    )
    parser.add_argument(
        'options',
        type=str,
        nargs='*',
        help='Parameters of the mode'
    )

    args = parser.parse_args()
    command_string = "python ./{script_name}.py {args}".format(
        script_name=args.mode,
        args = " ".join(args.options)
    )
    
    os.system(command_string)