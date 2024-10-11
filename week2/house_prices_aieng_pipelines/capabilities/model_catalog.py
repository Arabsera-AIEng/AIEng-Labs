import os
import json
import joblib
import uuid
import numpy as np

class ModelCatalog:
    """
    A class for managing projects and models within a catalog. Each project has a unique UUID and can have multiple versions of models.
    """

    def __init__(self, catalog_path):
        """
        Initialize the ModelCatalog.

        Parameters:
        - catalog_path: str, the directory where projects and models are stored.
        """
        self.catalog_path = catalog_path
        if not os.path.exists(self.catalog_path):
            os.makedirs(self.catalog_path)
        self.catalog_file = os.path.join(self.catalog_path, "models.json")

        # Create an initial models.json file if it doesn't exist
        if not os.path.exists(self.catalog_file):
            initial_data = {"projects": []}
            with open(self.catalog_file, 'w') as f:
                json.dump(initial_data, f, indent=4)

    def create_or_retrieve_project(self, project_name):
        """
        Create a new project or retrieve the existing one based on the project name.

        Parameters:
        - project_name: str, name of the project (e.g., "House Price Prediction")

        Returns:
        - project_uuid: str, unique identifier for the project
        """
        with open(self.catalog_file, 'r') as f:
            catalog_data = json.load(f)

        # Search for the project in the catalog
        for project in catalog_data["projects"]:
            if project["project_name"] == project_name:
                return project["project_uuid"]

        # If project is not found, create a new one
        project_uuid = str(uuid.uuid4())
        new_project = {
            "project_name": project_name,
            "project_uuid": project_uuid,
            "stage": "dev",  # Default stage is set to 'dev'
            "versions": {}   # Dictionary to hold model versions
        }
        catalog_data["projects"].append(new_project)

        # Save the updated catalog back to the file
        with open(self.catalog_file, 'w') as f:
            json.dump(catalog_data, f, indent=4)

        return project_uuid

    def save_model(self, project_uuid, model, model_card, model_columns):
        """
        Save the model, model card, and model columns for a specific project version.
        The version is automatically determined based on the latest version available.

        Parameters:
        - project_uuid: str, unique identifier of the project
        - model: trained model object
        - model_card: dict, metadata about the model
        - model_columns: list, the columns used in the model
        """
        # Determine the next version number
        latest_version = self.get_latest_version(project_uuid)
        next_version = latest_version + 1

        # Find the project by UUID and create the version path
        project_path = os.path.join(self.catalog_path, project_uuid)
        if not os.path.exists(project_path):
            os.makedirs(project_path)

        # Create version directory if it doesn't exist
        version_path = os.path.join(project_path, str(next_version))
        if not os.path.exists(version_path):
            os.makedirs(version_path)

        # Save the model
        model_file = os.path.join(version_path, f"{project_uuid}_v{next_version}.pkl")
        joblib.dump(model, model_file)

        # Save the model card
        model_card_file = os.path.join(version_path, f"{project_uuid}_v{next_version}_card.json")
        with open(model_card_file, 'w') as f:
            json.dump(model_card, f, indent=4)

        # Save model columns
        columns_file = os.path.join(version_path, f"{project_uuid}_v{next_version}_columns.npy")
        np.save(columns_file, model_columns)

        # Update the models.json with project and version information
        self.update_catalog(project_uuid, next_version, model_card)

        print(f"Model, model card, and columns saved to {version_path}")

    def get_latest_version(self, project_uuid):
        """
        Retrieve the latest version number for a given project UUID.

        Parameters:
        - project_uuid: str, unique identifier of the project

        Returns:
        - latest_version: int, the latest version number (0 if no versions exist)
        """
        with open(self.catalog_file, 'r') as f:
            catalog_data = json.load(f)

        # Search for the project and find the latest version
        for project in catalog_data["projects"]:
            if project["project_uuid"] == project_uuid:
                versions = project.get("versions", {})
                if versions:
                    return max(int(v) for v in versions.keys())
                else:
                    return 0  # No versions exist yet
        return 0  # Project not found or no versions exist

    def update_catalog(self, project_uuid, version, model_card):
        """
        Update the models.json file with new version information for a given project UUID.

        Parameters:
        - project_uuid: str, unique identifier of the project
        - version: int, version of the model (e.g., "1", "v2")
        - model_card: dict, metadata about the model
        """
        # Load existing catalog data
        with open(self.catalog_file, 'r') as f:
            catalog_data = json.load(f)

        # Search for the project and update its version information
        for project in catalog_data["projects"]:
            if project["project_uuid"] == project_uuid:
                project["versions"][str(version)] = model_card
                break

        # Save the updated catalog back to file
        with open(self.catalog_file, 'w') as f:
            json.dump(catalog_data, f, indent=4)

    def load_model(self, project_uuid, version=None):
        """
        Load the model, model card, and model columns for a given project and version.

        Parameters:
        - project_uuid: str, unique identifier of the project
        - version: str or int, version of the model to load (if None, load the latest version)

        Returns:
        - model: loaded model object
        - model_card: dict, metadata about the model
        - model_columns: list, the columns used in the model
        """
        project_path = os.path.join(self.catalog_path, project_uuid)
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project directory {project_path} not found.")

        # Determine the latest version if version is not provided
        if version is None:
            version = self.get_latest_version(project_uuid)

        # Load the model
        version_path = os.path.join(project_path, str(version))
        model_file = os.path.join(version_path, f"{project_uuid}_v{version}.pkl")
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"Model file {model_file} not found.")
        model = joblib.load(model_file)

        # Load the model card
        model_card_file = os.path.join(version_path, f"{project_uuid}_v{version}_card.json")
        if not os.path.exists(model_card_file):
            raise FileNotFoundError(f"Model card file {model_card_file} not found.")
        with open(model_card_file, 'r') as f:
            model_card = json.load(f)

        # Load model columns
        columns_file = os.path.join(version_path, f"{project_uuid}_v{version}_columns.npy")
        if not os.path.exists(columns_file):
            raise FileNotFoundError(f"Model columns file {columns_file} not found.")
        model_columns = np.load(columns_file, allow_pickle=True)

        return model, model_card, model_columns

    def list_projects(self):
        """
        List all projects available in the catalog.

        Returns:
        - projects: list of project names and their UUIDs
        """
        with open(self.catalog_file, 'r') as f:
            catalog_data = json.load(f)
        return [{"project_name": project["project_name"], "project_uuid": project["project_uuid"]} for project in catalog_data["projects"]]

    def list_models(self, project_uuid):
        """
        List all models (versions) available for a given project by UUID.

        Returns:
        - versions: list of version numbers
        """
        with open(self.catalog_file, 'r') as f:
            catalog_data = json.load(f)
        for project in catalog_data["projects"]:
            if project["project_uuid"] == project_uuid:
                return list(project.get("versions", {}).keys())
        return []

    def get_features(self, project_uuid, version=None):
        """
        Get the list of features used by a given project and version.

        Parameters:
        - project_uuid: str, unique identifier of the project
        - version: str or int, version of the model (if None, get features for the latest version)

        Returns:
        - features: list of features
        """
        _, model_card, _ = self.load_model(project_uuid, version)
        return model_card.get("features", [])
