import pandas as pd
import configparser
from utils.path_helper import PathHelper

class DataLoader:
    def __init__(self, train_path, test_path):

        # Get absolute paths using PathHelper
        self.train_path = PathHelper.get_absolute_path(train_path)
        self.test_path = PathHelper.get_absolute_path(test_path)

    def load_data(self):
        train = pd.read_csv(self.train_path)
        test = pd.read_csv(self.test_path)
        return train, test
