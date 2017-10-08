#!/usr/bin/env python3
'''bootstrap
Install build system and required tools to build nonlibc.
DISCLAIMER: this is a hack!
In my defense, package management is f'ing HARD and there just
    seems to be nothing better than hand-coding the nitpicky
    cross-platform hand-waving for. each. dependecy.
COROLLARY: please DON'T just add another tool to this project;
    try and keep to what's there already.
THE GOOD NEWS: at least this bootstrap is now a python script
    (as opposed to BASH), so tooling is python3-only.
As always, the quest for a
    [Universal Install Script](https://www.explainxkcd.com/wiki/index.php/1654:_Universal_Install_Script)
    continues!
'''

import glob
import subprocess
import sys
import re
from shutil import which
from os import environ
import json

def run_cmd(args=[], shell=False, cwd=None, env={}):
    '''run_cmd()
    Run a command.
    Return stdout; raise an exception on failure.
    '''
    if verbose:
        print('EXEC: %s' % ' '.join(args))

    en = environ.copy()
    en.update(env)

    try:
        sub = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=shell, cwd=cwd, env=en, check=True);
    except subprocess.CalledProcessError as err:
        if verbose:
            print(err.stdout.decode('utf-8'))
            print(err.stderr.decode('utf-8'), file=sys.stderr)
        raise

    ret = sub.stdout.decode('utf-8')
    if verbose:
        print(ret)
    return ret.strip()

def vers(insane_input):
    '''vers()
    Takes a dodgy 'version_string' input
    Returns a list which can be compared (e.g. `>` `<` `==` etc.)
        with another list returned by this function.
    stolen from <https://stackoverflow.com/questions/1714027/version-number-comparison>
    '''
    # glean a version string
    try:
        version_string = re.match('\D*([\d.]+)', insane_input).group(1)
    except:
        raise ValueError('cannot find a version string in: %s' % insane_input)

    # listify it
    try:
        return [int(x) for x in re.sub(r'(\.0+)*$','', version_string).split(".")]
    except:
        raise ValueError('''cannot parse version string '%s' ''' % version_string)

class digest_json(object):
    ''' digested_json is an object that, when instantiated with a proper .json,
    creates all necessary attributes to build dependecies on that specific
    platform system.
    '''

    def __init__(self, json_data):
        ########################################################################
        # first we load our json data file and initialize some variables
        self.json_data = json_data
        self.linux_distro = None
        self.pkg_mgr = None
        self.packages = []
        ########################################################################
        # second we detect the platform we are on
        self.platform = sys.platform
        assert self.platform in self.json_data['platforms']
        print('Detected platform is: %s' % self.platform, file=sys.stderr)
        ########################################################################
        # third we try to identify the exact distro we are on
        if self.platform is 'linux':
            # loop through our registered linux distributions
            for distro in self.json_data['linux_distros']:
                for release_file in glob.glob('/etc/*release'):
                    # no need for try-except because if the file is found by glob
                    #+    there should be no problem opening it in read only mode
                    #+    if no file is found glob returns an empty list and the
                    #+    for loop do not even start
                    with open(release_file, 'r') as open_file:
                        if distro in open_file.lower():
                            self.linux_distro = disto
                            print('Detected distro is: %s' % self.linux_distro,
                                    file=sys.stderr)
                            open_file.close()
                            break
                        open_file.close()
                else:
                    print('Could not detect exact linux distribution.\n\
                            No distro-specific packets will be installed',
                            file=sys.stderr)
        ########################################################################
        # at this point we need to know which pkg manager to use, starting our
        #+    try with the default distribution's one (if present)
        if self.linux_distro is not None:
            if which(self.json_data['linux_distros'][self.linux_distro].get('default_pgk_mgr')) is not None:
                self.pkg_mgr = self.json_data['linux_distros'][self.linux_distro].get('default_pgk_mgr')
        # If the distro wasn't detected or did not have a default pkg manager:
        #+    try to loop through suitable pkg managers in order to find the first good one
        if self.pkg_mgr is None:
            print('Looping through available pkg managers entry in our json...',
                    file=sys.stderr)
            for mgr in self.json_data.get('pkg_mgrs'):
                if self.platform in self.json_data.get('pkg_mgrs').get(mgr).get('suitable_for'):
                    if which(mgr) is not None:
                        self.pkg_mgr = mgr
                        break
        # this assert statement can change if we build zip_install for everything
        #+    but we still need mkdir. wget, zip...
        assert self.pkg_mgr is not None
        print('Detected package manager is: %s' % self.pkg_mgr,
                file=sys.stderr)
        ########################################################################
        # pull specific commands out of the json_data
        self.update_cmd = self.json_data['pkg_mgrs'][self.pkg_mgr].get('update_cmd')
        # use index instead of get() to throw KeyError on a vital value and save an assert statement
        self.install_cmd = self.json_data['pkg_mgrs'][self.pkg_mgr]['install_cmd']
        ########################################################################
        # now let's build the needed packages list based on the data we have
        packages = self.json_data['platforms'][self.platform].get('pakages')
        if self.linux_distro is not None:
            packages.append(self.json_data['linux_distros'][self.linux_distro].get('pakages'))
        for pkg in packages:
            # if a proper name for the pkg_mgr could not be found,
            #+    we will get a KeyError
            self.packages.append(self.json_data['pkgs'][pkg]['pkg_name'][self.pkg_mgr])





# must be at least python 3.5
if vers(sys.version) < vers('3.5'):
    print('python version %s < minimum 3.5 required' % sys.version,
            file=sys.stderr)
    exit(1)

# TODO : check also which compiler and it's version.
