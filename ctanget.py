#!/usr/bin/env python
"""
Like wget, but more specific and less useful.

A utility script for fetching and installing Tex packages from CTAN
(Comprehensive Tex Archive Network)
"""
import os
import re
import subprocess
import sys
import tempfile
import urllib
import zipfile

from BeautifulSoup import BeautifulSoup
import requests

CTAN_SITE = 'http://www.ctan.org/'
CTAN_SEARCH = CTAN_SITE + 'search'

DOWNLOAD_DIR = '~/ctan_downloads/'
DOWNLOAD_DIR = os.path.expanduser(DOWNLOAD_DIR)

LATEX_INSTALL_DIR = '/usr/share/texmf/tex/latex/'


if len(sys.argv) <= 1:
    sys.exit("You have to supply the name of the thing you want to ctanget.")

search_form_data = (('search', sys.argv[1]),
                    ('search_type', 'filename'))
search_url = CTAN_SEARCH + '?' + urllib.urlencode(search_form_data)

# Get the page returned by the search
req = requests.get(search_url)
search_soup = BeautifulSoup(req.content)

# Get us all our links
links = search_soup.find('table', {'class': 'pkg_info'}).findAll('a')


for i, link in enumerate(links, start=1):
    print '%s  file: %s' % (i, link.string,)
    print '   link: %s' % (link.get('href'),)
print


# User chooses which file
try:
    selection = int(raw_input('Which should we download: '))
except ValueError:
    exit("What you typed was not an integer. Exiting.")


if not 0 < int(selection) <= i:
    exit("You must pick a number between 1 and %s" % (int(selection),))
selected_link = links[selection - 1]

if 'pkg' in selected_link.get('href'):
    # Parse webpage for the chosen file
    pkg_url = selected_link.get('href')
    if pkg_url.startswith('/'):
        pkg_url = CTAN_SITE + pkg_url

    pkg_req = requests.get(pkg_url)
    pkg_soup = BeautifulSoup(pkg_req.content)
    # Find the zip file at the end of this rainbow
    directory_url = pkg_soup.find('a', text=re.compile('CTAN directory$')).parent.get('href')

    if directory_url.startswith('/'):
        directory_url = CTAN_SITE + directory_url
    directory_req = requests.get(directory_url)
    directory_soup = BeautifulSoup(directory_req.content)
    zip_link = directory_soup.find('a', text=re.compile('zip file')).parent


zip_file_name = os.path.basename(zip_link.get('href').split('/')[-1])
print "Downloading %s" % (zip_file_name,)

# Download the zip file
zip_file_dir = tempfile.mkdtemp()
zip_file_path = os.path.join(zip_file_dir, zip_file_name)

with open(zip_file_path, 'w') as f:
    download_url = zip_link.get('href')
    if download_url.startswith('/'):
        download_url = CTAN_SITE + download_url
    download_req = requests.get(download_url)
    f.write(download_req.content)

zip_file = zipfile.ZipFile(zip_file_path)


# If a zipfile contains a directory with all files underneath it, use the
# directory name
import pdb; pdb.set_trace()

if not len([zip_file.namelist()[0] in zip_test for zip_test in zip_file.namelist()[1:]]):
    zip_file_dir = zip_file.namelist()[0]
else:
    zip_file_dir = zip_file_path.rstrip('.zip')


print "Extracting files to %s" % (zip_file_dir,)
zip_file.extractall(zip_file_dir)


# Copy extracted files into the latex dir
subprocess.Popen(['sudo', 'cp', '-r', zip_file_dir, LATEX_INSTALL_DIR])
# Run texhash
subprocess.Popen(['sudo', 'texhash'])
