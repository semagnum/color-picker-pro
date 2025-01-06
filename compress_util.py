import os
import logging
import zipfile
import ast

allowed_file_extensions = {'.py', '.md', '.toml', 'LICENSE'}

log = logging.getLogger(__name__)


def zipdir(path, ziph: zipfile.ZipFile, zip_subdir_name):
    for root, dirs, files in os.walk(path):
        for file in files:
            if any(file.endswith(ext) for ext in allowed_file_extensions):
                orig_hier = os.path.join(root, file)
                arc_hier = os.path.join(zip_subdir_name, orig_hier)
                ziph.write(orig_hier, arc_hier)
                log.debug(file + ' written to zip file')


def generate_zip_filename(addon_name):
    major, minor, patch = get_addon_version('__init__.py')
    return '{}-{}-{}-{}.zip'.format(addon_name, major, minor, patch)


def get_addon_version(init_path):
    with open(init_path, 'r') as f:
        node = ast.parse(f.read())

    n: ast.Module
    for n in ast.walk(node):
        for b in n.body:
            if isinstance(b, ast.Assign) and isinstance(b.value, ast.Dict) and (
                    any(t.id == 'bl_info' for t in b.targets)):
                bl_info_dict = ast.literal_eval(b.value)
                return bl_info_dict['version']
    raise ValueError('Cannot find bl_info')


def zip_main(addon_name):
    filename = generate_zip_filename(addon_name)
    try:
        zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
        zipdir('.', zipf, addon_name)
        zipf.close()
        log.info('Successfully created zip file: {}'.format(filename))
    except Exception as e:
        log.error('Failed to create {}: {}'.format(filename, e))
        exit(1)


if __name__ == '__main__':
    # TODO do not delete, still needed to zip for <4.1
    logging.basicConfig(level=logging.INFO)
    zip_main('color_picker_pro')
