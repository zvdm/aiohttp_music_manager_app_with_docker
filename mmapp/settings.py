from pathlib import Path
import yaml


__all__ = ('get_config', )

BASE_DIR = Path(__file__).parent.parent
config_path = BASE_DIR / 'config' / 'config_mmapp.yaml'


def get_config(path=None):
    with open(config_path) as f:
        conf = yaml.safe_load(f)

    cf_dict = {}
    if path:
        cf_dict = yaml.safe_load(path)

    conf.update(**cf_dict)

    return conf
