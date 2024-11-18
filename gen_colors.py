import io
import os
import sys
import toml
import time
import subprocess
from pathlib import PosixPath


def parse_config(file):
    return toml.load(file)


def write_to_config(file, format, name, value):
    file.write(format.format(name=name, value=value))


def parse_args():
    config = ''
    colors_file = ''
    parsing = ''
    watch = False
    for i in range(1, len(sys.argv)):
        match sys.argv[i]:
            case '-f':
                parsing = 'f'
            case '-c':
                parsing = 'c'
            case '-w':
                watch = True
            case _:
                match parsing:
                    case 'f':
                        colors_file = PosixPath(sys.argv[i])
                    case 'c':
                        config = PosixPath(sys.argv[i])
                    case _:
                        continue
    if config == '':
        config = PosixPath('~/.config/colorgen/config.toml')
    return config.expanduser(), colors_file.expanduser(), watch


def generate_colors(config, colors):
    for app in config['config']:
        appcon = config['config'][app]
        colorgen = config['colorgen']

        with io.open(PosixPath(colorgen['dir'], appcon['path']).expanduser(), 'w') as file:
            if 'base16' in appcon and appcon['base16']:
                file.write('scheme: ' + colors['base16']['scheme'] + '\n')
                file.write('author: ' + colors['base16']['author'] + '\n')
                for name in colors['base16']:
                    if name != 'scheme' and name != 'author':
                        value = colors['colors'][colors['base16'][name]]
                        file.write(appcon['format'].format(name=name, value=value) + '\n')
            else:
                if 'before' in appcon:
                    file.write(appcon['before'] + '\n')
                for name in colors['colors']:
                    value = colors['colors'][name]
                    file.write(appcon['format'].format(name=name, value=value) + '\n')
                if 'after' in appcon:
                    file.write(appcon['after'] + '\n')

        if colorgen['reload'] and 'reload' in appcon:
            os.system(appcon['reload'])



if __name__ == "__main__":
    config_file, colors_file, watch = parse_args()
    config = parse_config(config_file)
    colors = parse_config(colors_file)
    if watch:
        last_modified = os.path.getmtime(colors_file)
        while True:
            current_modified = os.path.getmtime(colors_file)
            if current_modified != last_modified:
                print('updating configs')
                colors = parse_config(colors_file)
                try:
                    generate_colors(config, colors)
                except Exception as e:
                    print('Error occured: ' + repr(e))
                last_modified = current_modified
            time.sleep(1)
    else:
        generate_colors(config, colors)
