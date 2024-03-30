from my_package.config.json_reader.ConfigReader import ConfigReader


def read_config(config_file_path):
    config_reader = ConfigReader(config_file_path)
    return config_reader.read_config()
