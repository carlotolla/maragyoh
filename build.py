# -*- coding: UTF8 -*-
from pybuilder.core import use_plugin, init, Author, task
import os
import sys

SRC = os.path.join(os.path.dirname(__file__), "src")
DOC = os.path.join(os.path.dirname(__file__), "doc")
sys.path.append(SRC)
sys.path.append(DOC)
from maragyoh import __version__

use_plugin("python.core")
use_plugin("python.install_dependencies")
use_plugin("python.unittest")
# use_plugin("python.coverage")
use_plugin("python.distutils")
# use_plugin('pypi:pybuilder_header_plugin')
use_plugin("exec")

url = 'https://github.com/cetoli/maragyoh'
description = "Please visit {url}".format(url=url)
authors = [Author('Carlo Oliveira', 'carlo@ufrj.br')]
license = 'GNU General Public License v3 (GPLv3)'
summary = "A Visual Outline Constructor"
version = __version__
default_task = ['analyze', 'publish', 'buid_docs']  # , 'post_docs']


# default_task = ['analyze']  # , 'post_docs']


@init
def initialize(project):
    project.set_property('distutils_classifiers', [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Bottle',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: Portuguese (Brazilian)',
        'Topic :: Education',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'])
    header = open('header.py').read()
    project.set_property('dir_source_main_python', 'src')
    project.set_property('dir_source_unittest_python', 'src/test')
    project.set_property('unittest_module_glob', 'test_*')
    # project.set_property('pybuilder_header_plugin_expected_header', header)
    project.set_property('pybuilder_header_plugin_break_build', True)


@task
def post_docs(project, logger):
    from subprocess import call
    result = call(['curl', '-X', 'POST', 'http://readthedocs.org/build/maragyoh'])
    logger.info("Commit hook @ http://readthedocs.org/build/maragyoh: %d" % result)


@task
def buid_docs(project, logger):
    from subprocess import check_output
    result = check_output(['make', '-C', DOC, 'html'])
    logger.info(result)


@task
def build_web(project, logger):
    from subprocess import check_output
    from distutils.dir_util import copy_tree, mkpath
    from shutil import rmtree, copy
    from os import chdir, path
    if path.isdir("src/maragyoh/views/build"):
        rmtree("src/maragyoh/views/build")
    r = mkpath("src/maragyoh/views/build")
    chdir("src/maragyoh/views/build")
    logger.info(r)
    r = check_output(['python3', '-m', "brython", '--install'])
    logger.info(r)
    r = mkpath("maragyoh")
    logger.info(r)
    copy_tree("../maragyoh", "maragyoh")
    r = copy("../.bundle-include", ".")
    logger.info(r)
    r = copy("../maragyoh.html", ".")
    result = check_output(['python3', '-m', "brython", '--modules'])
    logger.info(r)
    logger.info(result)


if __name__ == "__main__":
    from subprocess import check_output
    result0 = check_output(['pyb', 'build_web'])
    [print(line) for line in str(result0).split("\\n")]
