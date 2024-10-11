import configparser
from capabilities.model_catalog import ModelCatalog


class ModelLoader:
    """
    Singleton class to load and provide access to the model, model card, and model columns.
    This class automatically loads the latest version of the model unless an explicit version is specified.
    """
    _instance = None

    def __new__(cls, config_path='../../config/fastapi_service_config.ini', project_name='House Price Prediction', version=None):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            # Read config file
            config = configparser.ConfigParser()
            config.read(config_path)

            model_catalog_path = config['paths']['model_catalog']

            cls._instance.model_catalog = ModelCatalog(catalog_path=model_catalog_path)

            # Create or retrieve the project UUID based on project name
            project_uuid = cls._instance.model_catalog.create_or_retrieve_project(project_name)
            cls._instance.project_uuid = project_uuid

            # Load the latest model version (or specific version if provided)
            cls._instance.model, cls._instance.model_card, cls._instance.model_columns = \
                cls._instance.model_catalog.load_model(project_uuid, version)

        return cls._instance
