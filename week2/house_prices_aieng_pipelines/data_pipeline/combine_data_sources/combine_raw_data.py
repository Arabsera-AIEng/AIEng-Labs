import configparser
import os
import pandas as pd
from utils.path_helper import PathHelper

class DataCombiner:
    def __init__(self, config_path='config.ini'):
        # Load the INI configuration file
        config = configparser.ConfigParser()
        config.read(config_path)

        # Convert relative paths to absolute paths using PathHelper
        self.input_dir = PathHelper.get_absolute_path(config['data_combiner']['input_dir'])
        self.output_dir = PathHelper.get_absolute_path(config['data_combiner']['output_dir'])
        self.key = config['data_combiner']['key']

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def combine_data_parts(self, part1_filename, part2_filename, output_filename):
        """
        Combine two data parts based on a common key and save the result.
        """
        # Construct full paths for the input files
        part1_path = os.path.join(self.input_dir, part1_filename)
        part2_path = os.path.join(self.input_dir, part2_filename)

        # Read the CSV parts
        part1 = pd.read_csv(part1_path)
        part2 = pd.read_csv(part2_path)

        # Merge the two parts on the specified key
        combined_df = pd.merge(part1, part2, on=self.key, how='inner')

        # Save the combined dataframe to the output directory
        combined_df.to_csv(os.path.join(self.output_dir, output_filename), index=False)
        print(f"Data parts combined and saved as {output_filename}.")
