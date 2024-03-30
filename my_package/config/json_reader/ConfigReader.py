import simplejson as json
import yaml


class ConfigReader:
    # Reader for both json and yaml files
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

    def read_config(self):
        try:
            with open(self.config_file_path, "r") as file:
                if self.config_file_path.endswith(".json"):
                    config_data = json.load(file)
                elif self.config_file_path.endswith(
                    ".yaml"
                ) or self.config_file_path.endswith(".yml"):
                    config_data = yaml.safe_load(file)
                else:
                    raise ValueError(
                        f"Unsupported file format: {self.config_file_path}"
                    )
            return config_data
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file '{self.config_file_path}' not found.")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Error parsing data in '{self.config_file_path}': {e}")
        except Exception as e:
            raise Exception(
                f"An error occurred while reading '{self.config_file_path}': {e}"
            )
