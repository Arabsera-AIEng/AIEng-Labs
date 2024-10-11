import pandas as pd
import os
import configparser
from utils.path_helper import PathHelper

class RawDataConsumer:
    def __init__(self, config_path='config.ini'):
        # Load the INI configuration file
        config = configparser.ConfigParser()
        config.read(config_path)

        # Convert relative paths to absolute paths
        self.train_path = PathHelper.get_absolute_path(config['data_consumer']['train_path'])
        self.test_path = PathHelper.get_absolute_path(config['data_consumer']['test_path'])
        self.output_dir = PathHelper.get_absolute_path(config['data_consumer']['output_dir'])

        # Create the output directory if not exists
        os.makedirs(self.output_dir, exist_ok=True)

    def split_data_sources(self):
        """
        Split the raw training and testing datasets into multiple sources.
        """
        train = pd.read_csv(self.train_path)
        test = pd.read_csv(self.test_path)

        # Split train and test into two parts each
        train_basic_info = train[['Id', 'MSSubClass', 'MSZoning', 'LotFrontage', 'LotArea', 'Street', 'Alley', 'LotShape', 'LandContour']]
        train_structure_info = train.drop(columns=train_basic_info.columns.difference(['Id']))

        test_basic_info = test[['Id', 'MSSubClass', 'MSZoning', 'LotFrontage', 'LotArea', 'Street', 'Alley', 'LotShape', 'LandContour']]
        test_structure_info = test.drop(columns=test_basic_info.columns.difference(['Id']))

        # Save the split data parts
        train_basic_info.to_csv(os.path.join(self.output_dir, 'train_part1.csv'), index=False)
        train_structure_info.to_csv(os.path.join(self.output_dir, 'train_part2.csv'), index=False)
        test_basic_info.to_csv(os.path.join(self.output_dir, 'test_part1.csv'), index=False)
        test_structure_info.to_csv(os.path.join(self.output_dir, 'test_part2.csv'), index=False)

        print("Raw data split into multiple sources successfully.")
