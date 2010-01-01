## Process this file with automake to produce Makefile.in

SUBDIRS = data po Perroquet

CLEANFILES=

bin_SCRIPTS = perroquet
CLEANFILES += perroquet


perroquet: perroquet.in
	sed -e s!\@PYTHON\@!@PYTHON@!		\
	    -e s!\@PYOPTIONS\@!-OOt!		\
	    < $< > $@
perroquet: Makefile

EXTRA_DIST = \
	perroquet.in \
	MAINTAINERS

