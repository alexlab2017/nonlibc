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
    platform and/or OS.

    Attributes are:

    self.json_data : this is a dict with all the "raw" .json data loaded
    self.detected_platform : sys.platform
    self.detected_os : this see if one of our registered os is the one we are on
        based on /etc/*release file (or files)
    self.needed_packages : needed packages based on os, platform and version
    self.pkg_manager : detected pkg manager

    '''

    def __init__(self, json_data):
        ########################################################################
        # first we load our json data file
        self.json_data = json_data
        ########################################################################
        # second we detect the platform we are on
        self.detected_platform = sys.platform
        ########################################################################
        # third we try to identify the exact distro we are using
        #+    could be 'Ubuntu', 'Fedora', etc.
        # if detected_platform is 'win32' we are on Windows.
        #+    per what I know there are no "flavours" of Windows
        #+    indeed there are different versions but for now we are not
        #+    considering this point
        if self.detected_platform != 'win32':
            # loop through our registered os
            for os in self.json_data.get('os'):
                for release_file in glob.glob('/etc/*release'):
                    # no need for try-except because if the file is found by glob
                    #+    there should be no problem opening it in read only mode
                    #+    if no file is found glob returns an empty list and the
                    #+    for loop do not even start
                    with open(release_file, 'r') as open_file:
                        if os in open_file.lower():
                            self.detected_os = os
                            open_file.close()
                            break
                        open_file.close()
                else:
                    print('Could not detect OS, "%s" platform will be used\n\
                    but no  OS-specific packet will be installed' % detected_platform,
                    file=sys.stderr)
        else:
            detected_os = 'windows'
        ########################################################################
        # at this point we need to know which pkg manager to use, starting our
        #+    try with the default "os"'s one (if present)
        # with this implementation it is not mandatory that an "os" has a default_pgk_mgr
        #+    but this is weird because linux/unix system always have this attribute
        #+    maybe I'll chage this section later on
        if self.detected_os:
            try:
                default_pgk_mgr = self.json_data.get('os').get(detected_os).get('default_pgk_mgr')
            except KeyError:
                print('No default pkg manager found.\n\
                Trying to find a suitable pkg manager...', file=sys.stderr)
            else:
                if which(default_pgk_mgr) not None:
                    self.detected_pkg_mgr = default_pgk_mgr
        # now : check if we have a valid pkg manager.
        # If the os wasn't detected or
        #+    did not have a default pkg manager or
        #+    the default pkg manager is not present on the system :
        #+        try to loop through suitable pkg managers in order to find the first good one
        if not hasattr(self, detected_pkg_mgr):




        # now let's build the needed packages list based on the data we have



# must be at least python 3.5
if vers(sys.version) < vers('3.5'):
	print('python version %s < minimum 3.5 required' % sys.version, file=sys.stderr)
	exit(1)
