# -*- coding: UTF8 -*-
from pybuilder.core import use_plugin, init, Author, task
import os
import sys
import requests
from lxml import html
import urllib3
from maragyoh import __version__


class HL:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


LOCAL_DIR = '/home/carlo/Documentos/dev/maragyoh/src/maragyoh/views/build/{}'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SEPARATOR = "# -- #" * 2
MSG = "{s}%s %s{u}%s ==> OK = %s{d}%s %s{s}".format(s=SEPARATOR, u="!s:<40", d="!s:<6")
MSG.format("---> <---".split())
MESG = MSG % ('--->', '{', '}', '{', '}', '<---')
RPRT = HL.OKBLUE + MSG % ('--->', '{', '}', '{', '}', '<---') + HL.ENDC
WARN = HL.WARNING + MSG % ('--[[', '{', '}', '{', '}', ']]--') + HL.ENDC
ERRR = HL.FAIL + MSG % ('XX[[', '{', '}', '{', '}', ']]XX') + HL.ENDC
OKGO = HL.OKGREEN + MSG % ('@@[[', '{', '}', '{', '}', ']]@@') + HL.ENDC

TAGS = ["activlet,source,brython"]

NOFILES = {}
DELETE = "https://activufrj.nce.ufrj.br/file/delete/carlo/{}"
ACTIV = "https://activufrj.nce.ufrj.br/{}"


def handle_remote_deploy(description_="instruções para o build", tags=TAGS, archive="README.txt", logger=print):
    s = requests.Session()
    req = {True: s.get, False: s.post}

    def request(url_, get=True, filer=NOFILES, **kwargs):
        result = req[get](url_, data=kwargs, files=filer, verify=False)
        tree = html.fromstring(result.content)
        data = {i.get('name'): i.get('value') for i in tree.cssselect('input')}
        desc = kwargs["desc__"] if "desc__" in kwargs else "POST END"
        msg = bytes(result.content).decode('utf8')
        error = '<div class="tnmHomeMSG">'
        if desc:
            logger(MESG.format(desc, result.ok))
        if not result.ok:
            msg = msg.split('<p class="erro">')[1].split('</p>')[1].split('<p class="mensagem">')[1]
            logger(ERRR.format(msg))
        elif error in msg:
            msg = msg.split(error)[1].split('</div>')[0]
            logger(ERRR.format(msg, False))

        return result, data

    r, data_ = request(ACTIV.format("login"), desc__="GET LOGIN PAGE")
    data_.update(user='carlo', passwd=str(os.getenv("ACTIVLOG", "wrogpass")))
    r, data_ = request(ACTIV.format("login"), get=False, desc__="DO THE LOGIN", **data_)
    r, data_ = request(ACTIV.format("file/carlo"), **data_)
    if '<a href="/file/info/carlo/{}">'.format(archive) in bytes(r.content).decode('utf8'):
        request(DELETE.format(archive), desc__="DELELE -> {}".format(archive), **data_)
    else:
        logger(WARN.format("NÃO REMOVEU {:.9} ".format(archive[-9:]), False))
    # archive = "brython.js"
    file_uri = LOCAL_DIR.format(archive)
    files = {'arquivo': open(file_uri, 'rb')}
    logger(RPRT.format(file_uri[-min(32, len(file_uri) - 1):], "UPLOAD"))
    r, data_ = request(ACTIV.format("file/upload/carlo"), desc__=None, **data_)
    [data_.pop(k) for k in "description tags".split()]
    request(ACTIV.format("file/upload/carlo"),
            get=False, filer=files, desc__="UPLOAD FILE", description=description_, tags=tags, **data_)


# handle_remote_deploy(archive="demo.html")


SRC = os.path.join(os.path.dirname(__file__), "src")
DOC = os.path.join(os.path.dirname(__file__), "doc")
sys.path.append(SRC)
sys.path.append(DOC)

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
    # header = open('header.py').read()
    project.set_property('dir_source_main_python', 'src')
    project.set_property('dir_source_unittest_python', 'src/test')
    project.set_property('unittest_module_glob', 'test_*')
    # project.set_property('pybuilder_header_plugin_expected_header', header)
    project.set_property('pybuilder_header_plugin_break_build', True)


@task
def post_docs(project, logger):
    assert project or logger
    from subprocess import call
    result = call(['curl', '-X', 'POST', 'http://readthedocs.org/build/maragyoh'])
    logger.info("Commit hook @ http://readthedocs.org/build/maragyoh: %d" % result)


@task
def buid_docs(project, logger):
    assert project or logger
    from subprocess import check_output
    result = check_output(['make', '-C', DOC, 'html'])
    logger.info(result)


@task
def build_web(project, logger):
    assert project or logger
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


@task
def deploy_web(project, logger):
    assert project or logger
    pass


if __name__ == "__main__":
    from subprocess import check_output

    result0 = check_output(['pyb', 'build_web'])
    [print(line) for line in str(result0).split("\\n")]
