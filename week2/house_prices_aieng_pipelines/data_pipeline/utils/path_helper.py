import os

class PathHelper:
    @staticmethod
    def get_absolute_path(relative_path):
        """
        Convert a relative path to an absolute path based on the current working directory.
        If the path is already absolute, return it as is.
        """
        if os.path.isabs(relative_path):
            return relative_path
        # Use current working directory to resolve relative paths
        return os.path.abspath(os.path.join(os.getcwd(), relative_path))
