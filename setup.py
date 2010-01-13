#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from distutils.dist import Distribution
from distutils.cmd import Command
from distutils.command.install_data import install_data
from distutils.command.build import build
from distutils.dep_util import newer
from distutils.log import warn, info, error, fatal
import glob
import os
import sys
import subprocess
import platform

from perroquetlib.config import *

PO_DIR = 'po'
MO_DIR = os.path.join('build', 'mo')

class PerroquetDist(Distribution):
  global_options = Distribution.global_options + [
    ("without-gettext", None, "Don't build/install gettext .mo files"),
    ("without-icon-cache", None, "Don't attempt to run gtk-update-icon-cache")]

  def __init__ (self, *args):
    self.without_gettext = False
    self.without_icon_cache = False
    Distribution.__init__(self, *args)


class BuildData(build):
  def run (self):
    build.run (self)

    if self.distribution.without_gettext:
      return

    for po in glob.glob (os.path.join (PO_DIR, '*.po')):
      lang = os.path.basename(po[:-3])
      mo = os.path.join(MO_DIR, lang, 'LC_MESSAGES/perroquet.mo')

      directory = os.path.dirname(mo)
      if not os.path.exists(directory):
        info('creating %s' % directory)
        os.makedirs(directory)

      if newer(po, mo):
        info('compiling %s -> %s' % (po, mo))
        try:
          rc = subprocess.call(['msgfmt', '-o', mo, po])
          if rc != 0:
            raise Warning, "msgfmt returned %d" % rc
        except Exception, e:
          error("Building gettext files failed.  Try setup.py --without-gettext [build|install]")
          error("Error: %s" % str(e))
          sys.exit(1)

    TOP_BUILDDIR='.'
    INTLTOOL_MERGE='intltool-merge'
    desktop_in='data/perroquet.desktop.in'
    desktop_data='data/perroquet.desktop'
    os.system ("C_ALL=C " + INTLTOOL_MERGE + " -d -u -c " + TOP_BUILDDIR +
               "/po/.intltool-merge-cache " + TOP_BUILDDIR + "/po " +
               desktop_in + " " + desktop_data)

class Uninstall(Command):
  description = "Attempt an uninstall from an install --record file"

  user_options = [('manifest=', None, 'Installation record filename')]

  def initialize_options(self):
    self.manifest = None

  def finalize_options(self):
    pass

  def get_command_name(self):
    return 'uninstall'

  def run(self):
    self.ensure_filename('manifest')
    try:
      try:
        f = open(self.manifest)
        files = [file.strip() for file in f]
      except IOError, e:
        raise DistutilsFileError("unable to open install manifest: %s", str(e))
    finally:
      f.close()

    for file in files:
      if os.path.isfile(file) or os.path.islink(file):
        info("removing %s" % repr(file))
        if not self.dry_run:
          try:
            os.unlink(file)
          except OSError, e:
            warn("could not delete: %s" % repr(file))
      elif not os.path.isdir(file):
        info("skipping %s" % repr(file))

    dirs = set()
    for file in reversed(sorted(files)):
      dir = os.path.dirname(file)
      if dir not in dirs and os.path.isdir(dir) and len(os.listdir(dir)) == 0:
        dirs.add(dir)
        # Only nuke empty Python library directories, else we could destroy
        # e.g. locale directories we're the only app with a .mo installed for.
        if dir.find("site-packages/") > 0:
          info("removing %s" % repr(dir))
          if not self.dry_run:
            try:
              os.rmdir(dir)
            except OSError, e:
              warn("could not remove directory: %s" % str(e))
        else:
          info("skipping empty directory %s" % repr(dir))


class InstallData(install_data):
  def run (self):
    self.data_files.extend (self._find_mo_files ())
    install_data.run (self)
    if not self.distribution.without_icon_cache:
      self._update_icon_cache ()
    self._update_mime_database()
    self._update_desktop_database()

  # We should do this on uninstall too
  def _update_icon_cache(self):
    info("running gtk-update-icon-cache")
    try:
      subprocess.call(["gtk-update-icon-cache", "-q", "-f", "-t", os.path.join(self.install_dir, "share/icons/hicolor")])
    except Exception, e:
      warn("updating the GTK icon cache failed: %s" % str(e))

  def _update_mime_database(self):
    info("running update-mime-database")
    try:
      subprocess.call(["update-mime-database",  os.path.join(self.install_dir, "share/mime")])
    except Exception, e:
      warn("updating mime database failed: %s" % str(e))

  def _update_desktop_database(self):
    info("running update-desktop-database")
    try:
      subprocess.call(["update-desktop-database",])
    except Exception, e:
      warn("updating desktop database failed: %s" % str(e))

  def _find_mo_files (self):
    data_files = []

    if not self.distribution.without_gettext:
      for mo in glob.glob (os.path.join (MO_DIR, '*', 'LC_MESSAGES/perroquet.mo')):
       lang = os.path.basename(os.path.dirname(os.path.dirname(mo)))
       dest = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
       data_files.append((dest, [mo]))

    return data_files


if platform.system() == 'FreeBSD':
  man_dir = 'man'
else:
  man_dir = 'share/man'

setup(name='perroquet',
      version=APP_VERSION,
      description='Perroquet, listening comprehension tutor ',
      author='Frédéric Bertolus',
      author_email='fred.bertolus@gmail.com',
      url='http://perroquet.b219.org',
      license='GNU GPL v3',
      scripts=['perroquet'],
      data_files=[
                  ('share/applications', ['data/perroquet.desktop']),
                  ('share/mime/packages', ['data/perroquet.xml']),
                  ('share/pixmaps', ['data/icons/48x48/apps/perroquet.png']),
                  ('share/icons/hicolor/scalable/apps', glob.glob('data/icons/scalable/apps/*.svg')),
                  ('share/icons/hicolor/16x16/apps', glob.glob('data/icons/16x16/apps/*.png')),
                  ('share/icons/hicolor/22x22/apps', glob.glob('data/icons/22x22/apps/*.png')),
                  ('share/icons/hicolor/24x24/apps', glob.glob('data/icons/24x24/apps/*.png')),
                  ('share/icons/hicolor/32x32/apps', glob.glob('data/icons/32x32/apps/*.png')),
                  ('share/icons/hicolor/48x48/apps', glob.glob('data/icons/48x48/apps/*.png')),
                  ('share/icons/hicolor/256x256/apps', glob.glob('data/icons/256x256/apps/*.png')),
                  ('share/icons/hicolor/scalable/mimetypes', glob.glob('data/icons/scalable/mimetypes/*.svg')),
          ('share/perroquet/', ['data/perroquet.ui']),
          ('share/perroquet/', ['data/perroquet.png']),
                 ],
      packages=['perroquetlib'],
      cmdclass={'build': BuildData, 'install_data': InstallData, 'uninstall': Uninstall},
      distclass=PerroquetDist
     )
