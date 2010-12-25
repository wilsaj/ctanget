#!/usr/bin/env python
"""
Like wget, but more specific and less useful.

A utility script for fetching and installing Tex packages from CTAN
(Comprehensive Tex Archive Network)
"""
from BeautifulSoup import BeautifulSoup
import os
import re
import sys
import subprocess
import urllib
import urllib2
import zipfile


CTAN_URL = 'http://www.ctan.org/search.html#byName'
CTAN_SITE = 'http://www.ctan.org/'
CTAN_SEARCH_URL = CTAN_SITE + '/cgi-bin/filenameSearch.py'

DOWNLOAD_DIR = '~/ctan_downloads/'
DOWNLOAD_DIR = os.path.expanduser(DOWNLOAD_DIR)

LATEX_INSTALL_DIR = '/usr/share/texmf/tex/latex/'


if len(sys.argv) <= 1:
    sys.exit("You have to supply the name of the thing you want to ctanget.")


search_form_data = (('filename',sys.argv[1]),)
search_form_data = (('filename','wrapfig'),)
search_data = urllib.urlencode(search_form_data)


# Get the page returned by the search
search_soup=BeautifulSoup(urllib2.urlopen(CTAN_SEARCH_URL, search_data).read())

# Get us all our links
links = search_soup.find('pre', {'class': 'filename_search_hits'}).findAll('a')


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
    exit("You must pick a number between 1 and %s" %s (int(selection),))
selected_link = links[selection-1]


if '.zip' not in selected_link.string:
    # Parse webpage for the chosen file
    selection_soup = BeautifulSoup(urllib2.urlopen(CTAN_SITE + selected_link.get('href'),).read())
    # Find the zip file at the end of this rainbow
    zip_link = selection_soup.find('a',text=re.compile('\.zip$')).parent
else:
    zip_link = selected_link

zip_file_name = os.path.basename(zip_link.text)
print "Downloading %s" % (zip_file_name,)


# Download the zip file
zip_file_path = DOWNLOAD_DIR + zip_file_name
with open(zip_file_path, 'w') as f:
    f.write(urllib2.urlopen(CTAN_SITE + zip_link.get('href')).read())
zip_file = zipfile.ZipFile(zip_file_path)


# If a zipfile contains a directory with all files underneath it, use the
# directory name
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
