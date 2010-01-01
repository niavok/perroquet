bin_SCRIPTS = perroquet.py

perroquetdir = $(prefix)/bin

perroquet_PYTHON = \
	core.py \
	exercice_manager.py \
	gui.py \
	sequence.py \
	subtitles_loader.py \
	video_player.py

uidir = $(datadir)/perroquet
ui_DATA = gui.xml

DISTCLEANFILES = \
   $(ui_DATA) \         
   $(bin_SCRIPTS)         

EXTRA_DIST =  \
    $(bin_SCRIPTS) \
    $(perroquet_PYTHON) \
    $(ui_DATA)



