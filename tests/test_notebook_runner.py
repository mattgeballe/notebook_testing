import sys
import platform
import os
import unittest
from glob import glob
from subprocess import check_call
import json


nb_dir = os.environ.get('NB_DIR')
if nb_dir is None:
    # When run manually
    folders = ["Notebooks", "Drafts"]
    # Find all subfolders in a folder which have notebooks
    nb_dir = []
    for f in folders:
        nb_dir += [x[0] for x in os.walk(f) if ".ipynb_checkpoints" not in x[0]][1:]
else:
    # When run in Travis
    nb_dir = [nb_dir]

print(nb_dir)


class NotebookRunner(unittest.TestCase):
    pass


def notebook_runner(nb):

    def run_nb(self=None):
        dname = os.path.dirname(sys.executable)
        if platform.system() == "Windows":
            jupyter_exe = os.path.join(dname, 'Scripts/jupyter')
        else:
            jupyter_exe = os.path.join(dname, 'jupyter')

        print("Executing {}".format(os.path.basename(nb)))
        topdir = os.path.split(os.path.dirname(__file__))[0]
        cmd = [jupyter_exe,
               'nbconvert',
               os.path.join(topdir, nb),
               '--ClearOutputPreprocessor.enabled=True',
               '--execute',
               '--ExecutePreprocessor.timeout=120',
               '--FilesWriter.build_directory="{}"'.format(os.path.split(nb)[0]),
               '--to',
               'html']

        print(cmd)
        check_call(cmd)

        # Clean Up
        # os.remove(os.path.basename(nb).replace(".ipynb",".html"))

    return run_nb


def set_generic_python_kernel(nb_file):
    nbFile = open(nb_file, 'r')
    data = json.load(nbFile)
    nbFile.close()

    if data['metadata']['kernelspec']['name'] != u'python':
        print(data['metadata']['kernelspec'])
        data['metadata']['kernelspec']['name'] = u'python'

        jsonFile = open(nb_file, "w")
        jsonFile.write(json.dumps(data))
        jsonFile.close()


for d in nb_dir:
    for nb in glob(os.path.join(d, "*ipynb")):
        print(nb)
        tname = "test__{}__{}".format(*os.path.split(nb))
        set_generic_python_kernel(nb)

        print(tname)
        tfunc = notebook_runner(nb)
        setattr(NotebookRunner, tname, tfunc)

        
