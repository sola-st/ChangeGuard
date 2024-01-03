import json
import os

from .Hyperparams import Hyperparams


class Metadata(object):
    def __init__(self):
        if os.path.exists(Hyperparams.metadata_file):
            with open(Hyperparams.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def update(self, d):
        """
        Updates the metadata dictionary with the key value pairs of the passed argument.
        Args:
            d: dictionary used to update the metadata dictionary
        """
        self.metadata.update(d)

    def get(self, key):
        """
        Returns the metadata value corresponding to the key argument.
        Args:
            key: key used to retrieve the corresponding metadata value from the metadata dictionary.

        Returns: Value corresponding to `key`

        """
        return self.metadata.get(key)

    def store(self):
        with open(Hyperparams.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=4)
