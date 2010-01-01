appdir = $(pythondir)/Perroquet
app_PYTHON = __init__.py \
	perroquet.py \
	core.py \
	exercice_manager.py \
	gui.py \
	sequence.py \
	subtitles_loader.py \
	video_player.py

nodist_app_PYTHON = config.py

config.py: config.py.in
	sed						\
		-e s!\@prefix\@!$(prefix)!		\
		-e s!\@datadir\@!$(datadir)!		\
		-e s!\@pkgdatadir\@!$(pkgdatadir)!	\
		-e s!\@libexecdir\@!$(libexecdir)!	\
		-e s!\@libdir\@!$(libdir)!		\
		-e s!\@PACKAGE\@!$(PACKAGE)!		\
		-e s!\@VERSION\@!$(VERSION)!		\
		-e s!\@GETTEXT_PACKAGE\@!$(GETTEXT_PACKAGE)!	\
		< $< > $@
config.py: Makefile

CLEANFILES = config.py
EXTRA_DIST = config.py.in

all-local: config.py
