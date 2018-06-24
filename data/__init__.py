from pathlib import Path

import yaml


CURRENT_DIR = Path(__file__).parent
DEFAULT_CONFIG_FILE = CURRENT_DIR / Path('data_structure.yaml')


def load_data(data_file: str) -> dict:
    """Load project data from yaml file.
    File data_structure.yaml contains default data structure.

    :param str data_file: a yaml file with sound recording equipment data
        (e.g. audio_interface or audio_interface.yaml or /absolute/path/config/audio_interface.yaml)
    :return: dict with data
    """
    with DEFAULT_CONFIG_FILE.open() as cf:
        conf = yaml.load(cf.read())

    if not data_file:
        raise ValueError('Configuration file not specified.')

    data_path = Path(data_file).with_suffix('.yaml')

    if not data_path.is_absolute():
        data_path = CURRENT_DIR / data_path

    if not data_path.exists():
        raise FileNotFoundError(f'Configuration file "{data_path}" not found!')

    with open(data_path, 'r', encoding='utf-8') as ecf:
        extra_conf = yaml.load(ecf.read())

    conf.update(extra_conf)

    return conf
