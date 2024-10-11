import configparser
import pandas as pd

class DataQualityChecker:
    def __init__(self, df, config_path='config.ini'):
        self.df = df

        # Load the INI configuration file
        config = configparser.ConfigParser()
        config.read(config_path)

        # You can extend this to read data quality-related configurations from the config file if needed

    def run_checks(self):
        quality_report = {}

        quality_report['missing_values'] = self.df.isnull().sum().sum()
        quality_report['duplicate_ids'] = self.df['Id'].duplicated().sum()
        numerical_columns = self.df.select_dtypes(include=[float, int]).columns
        quality_report['negative_values'] = (self.df[numerical_columns] < 0).sum().sum()

        print(f"Data Quality Report: {quality_report}")
        return quality_report
