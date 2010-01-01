#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import pygtk
pygtk.require('2.0')
import sys, os, errno
import gtk
import pango


REPONSE_AVANT = 0
REPONSE_ARRIERE = 1

livre_xpm = [
"16 16 6 1",
"       c None s None",
".      c black",
"X      c red",
"o      c yellow",
"O      c #808080",
"#      c white",
"                ",
"       ..       ",
"     ..XX.      ",
"   ..XXXXX.     ",
" ..XXXXXXXX.    ",
".ooXXXXXXXXX.   ",
"..ooXXXXXXXXX.  ",
".X.ooXXXXXXXXX. ",
".XX.ooXXXXXX..  ",
" .XX.ooXXX..#O  ",
"  .XX.oo..##OO. ",
"   .XX..##OO..  ",
"    .X.#OO..    ",
"     ..O..      ",
"      ..        ",
"                "]

def conversion_tsv_rvb(t, s, v):
    if s == 0.0:
        return (v, v, v)
    else:
        teinte = t * 6.0
        saturation = s
        valeur = v

        if teinte >= 6.0:
            teinte = 0.0

        f = teinte - int(teinte)
        p = valeur * (1.0 - saturation)
        q = valeur * (1.0 - saturation * f)
        t = valeur * (1.0 - saturation * (1.0 - f))

        iteinte = int(teinte)
        if iteinte == 0:
            return(valeur, t, p)
        elif iteinte == 1:
            return(q, valeur, p)
        elif iteinte == 2:
            return(p, valeur, t)
        elif iteinte == 3:
            return(p, q, valeur)
        elif iteinte == 4:
            return(t, p, valeur)
        elif iteinte == 5:
            return(valeur, p, q)

def teinte_couleur(teinte):
    if teinte > 1.0:
        raise ValueError

    t, s, v = conversion_tsv_rvb (teinte, 1.0, 1.0)
    return (t*65535, s*65535, v*65535)

class SelectionFichier(gtk.FileSelection):
    def __init__(self):
        gtk.FileSelection.__init__(self)
        self.resultat = False

    def rappel_ok(self, bouton):
        self.hide()
        if self.fonction_ok(self.get_filename()):
            self.destroy()
            self.resultat = True
        else:
            self.show()

    def run(self, parent, titre, fichier_depart, fonction):
        if fichier_depart:
            self.set_filename(fichier_depart)

        self.fonction_ok = fonction
        self.ok_button.connect("clicked", self.rappel_ok)
        self.cancel_button.connect("clicked", lambda x: self.destroy())
        self.connect("destroy", lambda x: gtk.main_quit())
        self.set_modal(True)
        self.show()
        gtk.main()
        return self.resultat

class Buffer(gtk.TextBuffer):
    NBRE_COULEURS = 16
    ECHELLE_PANGO = 1024

    def __init__(self):
        gtk.TextBuffer.__init__(self)
        tabledesbalises = self.get_tag_table()
        self.comptref = 0
        self.nomfichier = None
        self.sanstitre_num = -1
        self.balises_couleurs = []
        self.marqueur_cycle_couleurs = 0
        self.teinte_depart = 0.0

        for i in range(Buffer.NBRE_COULEURS):
            balise = self.create_tag()
            self.balises_couleurs.append(balise)

        #self.balise_invisible = self.create_tag(None, invisible=True)
        self.balise_non_editable= self.create_tag(editable=False,
                                                foreground="purple")
        self.balise_resultat = self.create_tag(foreground="red")

        tabulations = pango.TabArray(4, True)
        tabulations.set_tab(0, pango.TAB_LEFT, 10)
        tabulations.set_tab(1, pango.TAB_LEFT, 30)
        tabulations.set_tab(2, pango.TAB_LEFT, 60)
        tabulations.set_tab(3, pango.TAB_LEFT, 120)
        self.balise_tabs_perso = self.create_tag(tabs=tabulations, foreground="green")
        TestTexte.buffers.empiler(self)

    def nom_simple(self):
        if self.nomfichier:
            return os.path.basename(self.nomfichier)
        else:
            if self.sanstitre_num == -1:
                self.sanstitre_num = TestTexte.sanstitre_num
                TestTexte.sanstitre_num += 1

            if self.sanstitre_num == 1:
                return "Sans titre"
            else:
                return "Sans titre #%d" % self.sanstitre_num

    def nouv_nomfichier(self):
        for fenetre in TestTexte.fenetres:
            if fenetre.zonetexte.get_buffer() == self:
                fenetre.titre_fenetre()

    def recherche(self, chaine, fenetre, avant):
        # on retire la balise "resultat" du buffer entier
        debut, fin = self.get_bounds()
        self.remove_tag(self.balise_resultat, debut, fin)

        iter = self.get_iter_at_mark(self.get_insert())

        i = 0
        if chaine:
            if avant:
                while 1:
                    resultat = iter.forward_search(chaine, gtk.TEXT_SEARCH_TEXT_ONLY)
                    if not resultat:
                        break
                    debut_resultat, fin_resultat = resultat
                    i += 1
                    self.apply_tag(self.balise_resultat, debut_resultat, fin_resultat)
                    iter = fin_resultat
            else:
                while 1:
                    resultat = iter.backward_search(chaine, gtk.TEXT_SEARCH_TEXT_ONLY)
                    if not resultat:
                        break
                    debut_resultat, fin_resultat = resultat
                    i += 1
                    self.apply_tag(self.balise_resultat, debut_resultat, fin_resultat)
                    iter = debut_resultat

        dialogue = gtk.MessageDialog(fenetre,
                                     gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_INFO,
                                     gtk.BUTTONS_OK,
                                     "%d chaines trouvees et marquees en rouge." % i)

        dialogue.connect("response", lambda x,y: dialogue.destroy())

        dialogue.show()

    def recherche_avant(self, chaine, fenetre):
        self.recherche(chaine, fenetre, True)

    def recherche_arriere(self, chaine, fenetre):
        self.recherche(chaine, fenetre, False)

    def incr_comptref(self):
        self.comptref += 1

    def decr_comptref(self):
        self.comptref -= 1
        if self.comptref == 0:
            self.couleurs(False)
            TestTexte.buffers.remove(self)
            del self

    def cycle_couleurs(self):
        self.alterner_couleurs()
        return True

    def couleurs(self, activer):
        teinte = 0

        if (activer and self.marqueur_cycle_couleurs == 0):
            self.marqueur_cycle_couleurs = gtk.timeout_add(
                200, self.cycle_couleurs)
        elif (not activer and self.marqueur_cycle_couleurs != 0):
            gtk.timeout_remove(self.marqueur_cycle_couleurs)
            self.marqueur_cycle_couleurs = 0

        for balise in self.balises_couleurs:
            if activer:
                couleur = apply(TestTexte.tabledescouleurs.alloc_color,
                                teinte_couleur(teinte))
                balise.set_property("foreground_gdk", couleur)
            else:
                balise.set_property("foreground_set", False)
            teinte += 1.0 / Buffer.NBRE_COULEURS

    def alterner_couleurs(self):
        teinte = self.teinte_depart

        for balise in self.balises_couleurs:
            couleur = apply(TestTexte.tabledescouleurs.alloc_color,
                          teinte_couleur (teinte))
            balise.set_property("foreground_gdk", couleur)

            teinte += 1.0 / Buffer.NBRE_COULEURS
            if teinte > 1.0:
                teinte = 0.0

        self.teinte_depart += 1.0 / Buffer.NBRE_COULEURS
        if self.teinte_depart > 1.0:
            self.teinte_depart = 0.0

    def gest_evnmt_balises(self, balise, widget, evenement, iter):
        position = iter.get_offset()
        nom_balise = balise.get_property("name")
        if evenement.type == gtk.gdk.MOTION_NOTIFY:
            print "Mouvement au caractere %d, balise `%s'\n" % (position, nom_balise)
        elif evenement.type == gtk.gdk.BUTTON_PRESS:
            print "Bouton de la souris appuye au caractere %d, balise `%s'\n" % (position, nom_balise)
        elif evenement.type == gtk.gdk._2BUTTON_PRESS:
            print "Double clic au caractere %d, balise `%s'\n" % (position, nom_balise)
        elif evenement.type == gtk.gdk._3BUTTON_PRESS:
            print "Triple clic au caractere %d, balise `%s'\n" % (position, nom_balise)
        elif evenement.type == gtk.gdk.BUTTON_RELEASE:
            print "Bouton de la souris relache au caractere %d, balise `%s'\n" % (position, nom_balise)
        elif (evenement.type == gtk.gdk.KEY_PRESS or
              evenement.type == gtk.gdk.KEY_RELEASE):
            print "Appui sur une touche au caractere %d, balise `%s'\n" % (position, nom_balise)

        return False

    def init_balises(self):
        tabledescouleurs = TestTexte.tabledescouleurs
        couleur = tabledescouleurs.alloc_color(0, 0, 0xffff)
        balise = self.create_tag("texte_bleu",
                                 foreground_gdk=couleur,
                                 background='yellow',
                                 size_points=24.0)
        balise.connect("event", self.gest_evnmt_balises)

        couleur = tabledescouleurs.alloc_color(0xffff, 0, 0)
        balise = self.create_tag("texte_rouge",
                                 rise= -4*Buffer.ECHELLE_PANGO,
                                 foreground_gdk=couleur)
        balise.connect("event", self.gest_evnmt_balises)

        couleur = tabledescouleurs.alloc_color(0, 0xffff, 0)
        balise = self.create_tag("fond_vert",
                                 background_gdk=couleur,
                                 size_points=10.0)
        balise.connect("event", self.gest_evnmt_balises)

        balise = self.create_tag("texte_barre",
                                 strikethrough=True)
        balise.connect("event", self.gest_evnmt_balises)

        balise = self.create_tag("souligne",
                                 underline=pango.UNDERLINE_SINGLE)
        balise.connect("event", self.gest_evnmt_balises)

        balise = self.create_tag("centre",
                                 justification=gtk.JUSTIFY_CENTER)

        balise = self.create_tag("droite-gauche",
                                 wrap_mode=gtk.WRAP_WORD,
                                 direction=gtk.TEXT_DIR_RTL,
                                 indent=30,
                                 left_margin=20,
                                 right_margin=20)

        balise = self.create_tag("indentation_neg",
                                 indent=-25)

    def remplir_buffer_exmpl(self):
        tabledesbalises = self.get_tag_table()
        if not tabledesbalises.lookup("texte_bleu"):
            self.init_balises()
        iter = self.get_iter_at_offset(0)
        ancrage = self.create_child_anchor(iter)
        self.set_data("ancrage", ancrage)
        pixbuf = gtk.gdk.pixbuf_new_from_xpm_data(livre_xpm)
        #pixbuf = gtk.gdk.pixbuf_new_from_file('livre.xpm')

        for i in range(100):
            iter = self.get_iter_at_offset(0)
            self.insert_pixbuf(iter, pixbuf)

            chaine = "%d Salut tout le monde ! bla bla bla bla bla bla bla bla bla bla bla bla\nhop lÃ  hop lÃ  hop lÃ  hop lÃ  hop lÃ  hop lÃ  hop lÃ  hop lÃ \n" % i
            self.insert(iter, chaine)

            iter = self.get_iter_at_line_offset(0, 5)
            self.insert(iter,
                          "(Salut tout le monde !)\nÃ±aca Ã±aca Salut, voilÃ  du texte pour tester le retour Ã  la ligne automatique, et avec de la ponctuation et accents s'il vous plaÃ®t ! Super, bla-bla - hmm, ouais.\nallez, une nouvelle ligne avec pas mal de texte. Y'a vraiment pas mal de texte... Du texte ! Encore du texte !\n"
                          "Allemand (Deutsch SÃ¼d) GrÃ¼ÃŸ Gott Grec (Î•Î»Î»Î·Î½Î¹ÎºÎ¬) Î“ÎµÎ¹Î¬ ÏƒÎ±Ï‚ HÃ©breu(×©×œ×•×) Ponctuation hÃ©braÃ¯que(\xd6\xbf×©\xd6\xbb\xd6\xbc\xd6\xbb\xd6\xbf×œ\xd6\xbc×•\xd6\xbc\xd6\xbb\xd6\xbb\xd6\xbf×\xd6\xbc\xd6\xbb\xd6\xbf) Japonais (æ—¥æœ¬èªž) ThaÃ¯ (à¸ªà¸§à¸±à¸ªà¸”à¸µà¸„à¸£à¸±à¸š) CaractÃ¨res thaÃ¯s (à¸„à¸³à¸•à¹ˆà¸­à¹„à¸›à¸™à¸·à¹ˆà¸ªà¸°à¸à¸”à¸œà¸´à¸” à¸žà¸±à¸±à¹‰à¸±à¸±à¹ˆà¸‡à¹‚à¸à¸°)\n")

            marque_temp = self.create_mark("marque_tmp", iter, True);

            iter = self.get_iter_at_line_offset(0, 6)
            iter2 = self.get_iter_at_line_offset(0, 13)
            self.apply_tag_by_name("texte_bleu", iter, iter2)

            iter = self.get_iter_at_line_offset(1, 10)
            iter2 = self.get_iter_at_line_offset(1, 16)
            self.apply_tag_by_name("souligne", iter, iter2)

            iter = self.get_iter_at_line_offset(1, 14)
            iter2 = self.get_iter_at_line_offset(1, 24)
            self.apply_tag_by_name("texte_barre", iter, iter2)

            iter = self.get_iter_at_line_offset(0, 9)
            iter2 = self.get_iter_at_line_offset(0, 16)
            self.apply_tag_by_name("fond_vert", iter, iter2)

            iter = self.get_iter_at_line_offset(4, 2)
            iter2 = self.get_iter_at_line_offset(4, 10)
            self.apply_tag_by_name("fond_vert", iter, iter2)

            iter = self.get_iter_at_line_offset(4, 8)
            iter2 = self.get_iter_at_line_offset(4, 15)
            self.apply_tag_by_name("texte_rouge", iter, iter2)

            iter = self.get_iter_at_mark(marque_temp)
            self.insert(iter, "Texte centrÃ© !\n")

            iter2 = self.get_iter_at_mark(marque_temp)
            self.apply_tag_by_name("centre", iter2, iter)

            self.move_mark(marque_temp, iter)
            self.insert(iter, "Droite->gauche + retour Ã  la ligne auto\n")
            self.insert(iter, "ÙˆÙ‚Ø¯ Ø¨Ø¯Ø£ Ø«Ù„Ø§Ø« Ù…Ù† Ø£ÙƒØ«Ø± Ø§Ù„Ù…Ø¤Ø³Ø³Ø§Øª ØªÙ‚Ø¯Ù…Ø§ ÙÙŠ Ø´Ø¨ÙƒØ© Ø§ÙƒØ³ÙŠÙˆÙ† Ø¨Ø±Ø§Ù…Ø¬Ù‡Ø§ ÙƒÙ…Ù†Ø¸Ù…Ø§Øª Ù„Ø§ ØªØ³Ø¹Ù‰ Ù„Ù„Ø±Ø¨Ø­ØŒ Ø«Ù… ØªØ­ÙˆÙ„Øª ÙÙŠ Ø§Ù„Ø³Ù†ÙˆØ§Øª Ø§Ù„Ø®Ù…Ø³ Ø§Ù„Ù…Ø§Ø¶ÙŠØ© Ø¥Ù„Ù‰ Ù…Ø¤Ø³Ø³Ø§Øª Ù…Ø§Ù„ÙŠØ© Ù…Ù†Ø¸Ù…Ø©ØŒ ÙˆØ¨Ø§ØªØª Ø¬Ø²Ø¡Ø§ Ù…Ù† Ø§Ù„Ù†Ø¸Ø§Ù… Ø§Ù„Ù…Ø§Ù„ÙŠ ÙÙŠ Ø¨Ù„Ø¯Ø§Ù†Ù‡Ø§ØŒ ÙˆÙ„ÙƒÙ†Ù‡Ø§ ØªØªØ®ØµØµ ÙÙŠ Ø®Ø¯Ù…Ø© Ù‚Ø·Ø§Ø¹ Ø§Ù„Ù…Ø´Ø±ÙˆØ¹Ø§Øª Ø§Ù„ØµØºÙŠØ±Ø©. ÙˆØ£Ø­Ø¯ Ø£ÙƒØ«Ø± Ù‡Ø°Ù‡ Ø§Ù„Ù…Ø¤Ø³Ø³Ø§Øª Ù†Ø¬Ø§Ø­Ø§ Ù‡Ùˆ Â»Ø¨Ø§Ù†ÙƒÙˆØ³ÙˆÙ„Â« ÙÙŠ Ø¨ÙˆÙ„ÙŠÙÙŠØ§.\n")
            iter2 = self.get_iter_at_mark(marque_temp)
            self.apply_tag_by_name("droite-gauche", iter2, iter)

            self.insert_with_tags(iter,
                                    "Paragraphe avec indentation nÃ©gative. bla bla bla bla bla bla. Portez ce whisky au vieux juge blond qui fume.\n",
                                    self.get_tag_table().lookup("indentation_neg"))

        print "%d lignes %d caracteres\n" % (self.get_line_count(),
                                       self.get_char_count())

        # On deplace le curseur au debut
        iter = self.get_iter_at_offset(0)
        self.place_cursor(iter)
        self.set_modified(False)

    def remplir_buffer_fichier(self, nomfichier):
        try:
            f = open(nomfichier, "r")
        except IOError, (num_err, msg_err):
            erreur = "Impossible d'ouvrir le fichier '%s': %s" % (nomfichier, msg_err)
            fenetre = TestTexte.pile_fenetre_active.recuperer()
            dialogue = gtk.MessageDialog(fenetre, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_INFO,
                                       gtk.BUTTONS_OK, erreur);
            resultat = dialogue.run()
            dialogue.destroy()
            return False

        iter = self.get_iter_at_offset(0)
        buf = f.read()
        f.close()
        self.set_text(buf)
        self.set_modified(False)
        return True

    def buffer_enregistrer(self):
        resultat = False
        svg_ok = False
        if not self.nomfichier:
            return False

        nomfichier_svg = self.nomfichier + "~"
        try:
            os.rename(self.nomfichier, nomfichier_svg)
        except (OSError, IOError), (num_err, msg_err):
            if num_err != errno.ENOENT:
                erreur = "Impossible de creer une copie de sauvegarde '%s' de '%s': %s" % (nomfichier_svg,
                                                                                           self.nomfichier,
                                                                                           msg_err)
                fenetre = TestTexte.pile_fenetre_active.recuperer()
                dialogue = gtk.MessageDialog(fenetre, gtk.DIALOG_MODAL,
                                             gtk.MESSAGE_INFO,
                                             gtk.BUTTONS_OK, erreur);
                dialogue.run()
                dialogue.destroy()
                return False

        svg_ok = True
        debut, fin = self.get_bounds()
        caracteres = self.get_slice(debut, fin, False)
        try:
            file = open(self.nomfichier, "w")
            file.write(caracteres)
            file.close()
            resultat = True
            self.set_modified(False)
        except IOError, (num_err, msg_err):
            erreur = "Erreur d'ecriture dans '%s': %s" % (self.nomfichier, msg_err)
            fenetre = TestTexte.pile_fenetre_active.recuperer()
            dialogue = gtk.MessageDialog(fenetre, gtk.DIALOG_MODAL,
                                         gtk.MESSAGE_INFO,
                                         gtk.BUTTONS_OK, erreur);
            dialogue.run()
            dialogue.destroy()

        if not resultat and svg_ok:
            try:
                os.rename(nomfichier_svg, self.nomfichier)
            except OSError, (num_err, msg_err):
                erreur = "Impossible de restaurer la copie de sauvegarde '%s' de '%s': %s\nLa copie de sauvegarde '%s' n'a pas ete modifiee." % (
                nomfichier_svg, self.nomfichier, msg_err, nomfichier_svg)
                fenetre = TestTexte.pile_fenetre_active.recuperer()
                dialogue = gtk.MessageDialog(fenetre, gtk.DIALOG_MODAL,
                                             gtk.MESSAGE_INFO,
                                             gtk.BUTTONS_OK, erreur);
                dialogue.run()
                dialogue.destroy()

        return resultat

    def enregistrer_sous_ok(self, nomfichier):
        ancien_nomfichier = self.nomfichier

        if (not self.nomfichier or nomfichier != self.nomfichier):
            if os.path.exists(nomfichier):
                erreur = "Ecraser le fichier existant '%s'?"  % nomfichier
                fenetre = TestTexte.pile_fenetre_active.recuperer()
                dialogue = gtk.MessageDialog(fenetre, gtk.DIALOG_MODAL,
                                             gtk.MESSAGE_QUESTION,
                                             gtk.BUTTONS_YES_NO, erreur);
                resultat = dialogue.run()
                dialogue.destroy()
                if resultat != gtk.RESPONSE_YES:
                    return False

        self.nomfichier = nomfichier

        if self.buffer_enregistrer():
            self.nouv_nomfichier()
            return True
        else:
            self.nomfichier = ancien_nomfichier
            return False

    def buffer_enregistrer_sous(self):
        return SelectionFichier().run(self, "Enregistrer sous...", None, self.enregistrer_sous_ok)

    def verif_buffer_enreg(self):
        if self.get_modified():
            nom_simple = self.nom_simple()
            msg = "Enregistrer les modifications apportees a '%s'?" % nom_simple
            fenetre = TestTexte.pile_fenetre_active.recuperer()
            dialogue = gtk.MessageDialog(fenetre, gtk.DIALOG_MODAL,
                                         gtk.MESSAGE_QUESTION,
                                         gtk.BUTTONS_YES_NO, msg);
            dialogue.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            resultat = dialogue.run()
            dialogue.destroy()
            if resultat == gtk.RESPONSE_YES:
                if self.nomfichier:
                    return self.buffer_enregistrer()
                return self.buffer_enregistrer_sous()
            elif resultat == gtk.RESPONSE_NO:
                return True
            else:
                return False
        else:
            return True

class Fenetre(gtk.Window):
    def __init__(self, buffer=None):
        menus = [
            ( "/_Fichier", None, None, 0, "<Branch>" ),
            ( "/Fichier/_Nouveau", "<control>N", self.nouveau, 0, None ),
            ( "/Fichier/Nou_velle fenetre", None, self.nouvelle_fenetre, 0, None ),
            ( "/Fichier/_Ouvrir", "<control>O", self.ouvrir, 0, None ),
            ( "/Fichier/_Enregistrer", "<control>S", self.enregistrer, 0, None ),
            ( "/Fichier/Enregistrer _sous...", None, self.enregistrer_sous, 0, None ),
            ( "/Fichier/sep1", None, None, 0, "<Separator>" ),
            ( "/Fichier/_Fermer", "<control>W" , self.fermer, 0, None ),
            ( "/Fichier/_Quitter", "<control>Q" , self.quitter, 0, None ),
            ( "/_Edition", None, None, 0, "<Branch>" ),
            ( "/Edition/Rechercher...", None, self.rechercher, 0, None ),
            ( "/_Options", None, None, 0, "<Branch>" ),
            ( "/Options/Pas de retour a la ligne auto", None, self.change_retour, gtk.WRAP_NONE, "<RadioItem>" ),
            ( "/Options/Retour a la ligne apres mot", None, self.change_retour, gtk.WRAP_WORD, "/Options/Pas de retour a la ligne auto" ),
            ( "/Options/Retour a la ligne apres caractere", None, self.change_retour, gtk.WRAP_CHAR, "/Options/Pas de retour a la ligne auto" ),
            ( "/Options/sep1", None, None, 0, "<Separator>" ),
            ( "/Options/Editable", None, self.change_opt_editable, True, "<RadioItem>" ),
            ( "/Options/Non editable", None, self.change_opt_editable, False, "/Options/Editable" ),
            ( "/Options/sep1", None, None, 0, "<Separator>" ),
            ( "/Options/Afficher curseur", None, self.change_curseur_visible, True, "<RadioItem>" ),
            ( "/Options/Masquer curseur", None, self.change_curseur_visible, False, "/Options/Afficher curseur" ),
            ( "/Options/sep1", None, None, 0, "<Separator>" ),
            ( "/Options/De gauche a droite", None, self.change_direction, gtk.TEXT_DIR_LTR, "<RadioItem>" ),
            ( "/Options/De droite a gauche", None, self.change_direction, gtk.TEXT_DIR_RTL, "/Options/De gauche a droite" ),
            ( "/Options/sep1", None, None, 0, "<Separator>" ),
            ( "/Options/Espacement normal", None, self.change_espacement, False, "<RadioItem>" ),
            ( "/Options/Espacement funky", None, self.change_espacement, True, "/Options/Espacement normal" ),
            ( "/Options/sep1", None, None, 0, "<Separator>" ),
            ( "/Options/Ne pas alterner les couleurs", None, self.change_alterner_couleurs, False, "<RadioItem>" ),
            ( "/Options/Alterner les balises de couleur", None, self.change_alterner_couleurs, True, "/Options/Ne pas alterner les couleurs" ),
            ( "/_Attributs", None, None, 0, "<Branch>" ),
            ( "/Attributs/Editable", None, self.change_attr_editable, True, None ),
            ( "/Attributs/Non editable", None, self.change_attr_editable, False, None ),
            ( "/Attributs/Invisible", None, self.change_visible, False, None ),
            ( "/Attributs/Visible", None, self.change_visible, True, None ),
            ( "/Attributs/Tabulations personnalisees", None, self.change_tabulations, False, None ),
            ( "/Attributs/Tabulations par defaut", None, self.change_tabulations, True, None ),
            ( "/Attributs/Alternance de couleurs", None, self.change_appliquer_couleurs, True, None ),
            ( "/Attributs/Pas de couleurs", None, self.change_appliquer_couleurs, False, None ),
            ( "/Attributs/Retirer toutes les balises", None, self.retirer_balises, 0, None ),
            ( "/Attributs/Proprietes", None, self.proprietes, 0, None ),
            ( "/_Test", None, None, 0, "<Branch>" ),
            ( "/Test/_Exemple", None, self.exemple, 0, None ),
            ( "/Test/_Inserer et defiler", None, self.inserer_defiler, 0, None ),
            ( "/Test/_Ajouter objets enfants a deplacer", None, self.ajouter_enfants, 0, None ),
            ( "/Test/A_jouter objets enfants avec focus", None, self.ajouter_enfants_focus, 0, None ),
            ]

        if not buffer:
            buffer = Buffer()
        gtk.Window.__init__(self)

        TestTexte.fenetres.empiler(self)

        buffer.incr_comptref()

        if not TestTexte.tabledescouleurs:
            TestTexte.tabledescouleurs = self.get_colormap()

        self.connect("delete_event", self.evnmt_delete)

        self.raccourcis_clavier = gtk.AccelGroup()
        self.barremenus = gtk.ItemFactory(gtk.MenuBar, "<main>",
                                          self.raccourcis_clavier)
        self.barremenus.set_data("fenetre", self)
        self.barremenus.create_items(menus)

        self.add_accel_group(self.raccourcis_clavier)

        boitev = gtk.VBox(False, 0)
        self.add(boitev)

        boitev.pack_start(self.barremenus.get_widget("<main>"),
                          False, False, 0)

        fen_deroulante = gtk.ScrolledWindow()
        fen_deroulante.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.zonetexte = gtk.TextView(buffer)
        self.zonetexte.set_wrap_mode(gtk.WRAP_WORD)

        # On s'assure que l'on peut bien regler la largeur des bordures
        # Pas de veritable raison pour ceci, si ce n'est de tester.
        self.zonetexte.set_border_width(10)

        # Affichage des tabulations dans les fenetres superieure et inferieure
        self.zonetexte.set_border_window_size(gtk.TEXT_WINDOW_TOP, 15)
        self.zonetexte.set_border_window_size(gtk.TEXT_WINDOW_BOTTOM, 15)

        self.zonetexte.connect("expose_event", self.reaffichage_tabs)

        self.bhid = buffer.connect("mark_set", self.rappel_mvt_curseur)

        # Affichage des numeros des lignes dans les fenetres laterales; on devrait
        # quand meme fixer leur largeur de maniere un peu plus "scientifique".
        self.zonetexte.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, 30)
        self.zonetexte.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 30)

        self.zonetexte.connect("expose_event", self.affichage_num_lignes)

        boitev.pack_start(fen_deroulante, True, True, 0)
        fen_deroulante.add(self.zonetexte)

        self.set_default_size(500, 500)
        self.zonetexte.grab_focus()

        self.titre_fenetre()
        self.init_menus()
        self.ajouter_widgets_exemples()

        self.show_all()

    def evnmt_delete(self, fenetre, evenement, donnees=None):
        TestTexte.pile_fenetre_active.empiler(self)
        self.verif_fermer_fenetre()
        TestTexte.pile_fenetre_active.depiler()
        return True
    #
    # Fonctions de rappel des menus
    #
    def fenetre_vierge(self):
        buffer = self.zonetexte.get_buffer()
        if (not buffer.nomfichier and not buffer.get_modified()):
            return self
        else:
            return Fenetre(Buffer())

    def fenetre_widget(widget):
        if isinstance(widget, gtk.MenuItem):
            item_factory = gtk.item_factory_from_widget(widget)
            return item_factory.get_data("fenetre")
        else:
            app = widget.get_toplevel()
            return app.get_data("fenetre")

    def nouveau(self, action, widget):
        Fenetre()

    def nouvelle_fenetre(self, action, widget):
        Fenetre(self.zonetexte.get_buffer())

    def ouvrir_ok(self, nomfichier):
        nouv_fenetre = self.fenetre_vierge()
        buffer = nouv_fenetre.zonetexte.get_buffer()
        if not buffer.remplir_buffer_fichier(nomfichier):
            if nouv_fenetre != self:
                nouv_fenetre.fermer_fenetre()
            return False
        else:
            buffer.nomfichier = nomfichier
            buffer.nouv_nomfichier()
            return True;

    def ouvrir(self, action, widget):
        SelectionFichier().run(self, "Ouvrir un fichier...", None, self.ouvrir_ok)

    def enregistrer_sous(self, action, widget):
        TestTexte.pile_fenetre_active.empiler(self)
        self.zonetexte.get_buffer().buffer_enregistrer_sous()
        TestTexte.pile_fenetre_active.depiler()

    def enregistrer(self, action, widget):
        TestTexte.pile_fenetre_active.empiler(self)
        buffer = self.zonetexte.get_buffer()
        if not buffer.nomfichier:
            self.enregistrer_sous(donnees_rappel, action)
        else:
            buffer.buffer_enregistrer()
            TestTexte.pile_fenetre_active.depiler()

    def fermer(self, action, widget):
        TestTexte.pile_fenetre_active.empiler(self)
        self.verif_fermer_fenetre()
        TestTexte.pile_fenetre_active.depiler()

    def quitter(self, action, widget):
        TestTexte.pile_fenetre_active.empiler(self)
        for tmp in TestTexte.buffers:
            if not tmp.verif_buffer_enreg():
                return

        gtk.main_quit()
        TestTexte.pile_fenetre_active.depiler()

    def exemple(self, action, widget):
        nouv_fenetre = self.fenetre_vierge()
        buffer = nouv_fenetre.zonetexte.get_buffer()
        buffer.remplir_buffer_exmpl()

        nouv_fenetre.ajouter_widgets_exemples()

    def inserer_defiler(self, action, widget):
        buffer = self.zonetexte.get_buffer()

        debut, fin = buffer.get_bounds()
        marque = buffer.create_mark(None, fin, False)

        buffer.insert(fin,
                      "Salut ! Voici plusieurs lignes de texte\n"
                      "Ligne 1\n"  "Ligne 2\n"
                      "Ligne 3\n"  "Ligne 4\n"
                      "Ligne 5\n")

        self.zonetexte.scroll_to_mark(marque, 0, True, 0.0, 1.0)
        buffer.delete_mark(marque)

    def change_retour(self, action, widget):
        self.zonetexte.set_wrap_mode(action)

    def change_direction(self, action, widget):
        self.zonetexte.set_direction(action)
        self.zonetexte.queue_resize()

    def change_espacement(self, action, widget):
        if action:
            self.zonetexte.set_pixels_above_lines(23)
            self.zonetexte.set_pixels_below_lines(21)
            self.zonetexte.set_pixels_inside_wrap(9)
        else:
            self.zonetexte.set_pixels_above_lines(0)
            self.zonetexte.set_pixels_below_lines(0)
            self.zonetexte.set_pixels_inside_wrap(0)

    def change_opt_editable(self, action, widget):
        self.zonetexte.set_editable(action)

    def change_curseur_visible(self, action, widget):
        self.zonetexte.set_cursor_visible(action)

    def change_alterner_couleurs(self, action, widget):
        self.zonetexte.get_buffer().couleurs(action)

    def change_attr_editable(self, action, widget):
        buffer = self.zonetexte.get_buffer()
        limites = buffer.get_selection_bounds()
        if limites:
            debut, fin = limites
            if action:
                buffer.remove_tag(buffer.balise_non_editable, debut, fin)
            else:
                buffer.apply_tag(buffer.balise_non_editable, debut, fin)

    def change_visible(self, action, widget):
        buffer = self.zonetexte.get_buffer()
        limites = buffer.get_selection_bounds()
        if limites:
            debut, fin = limites
            if action:
                buffer.remove_tag(buffer.balise_invisible, debut, fin)
            else:
                buffer.apply_tag(buffer.balise_invisible, debut, fin)

    def change_tabulations(self, action, widget):
        buffer = self.zonetexte.get_buffer()
        limites = buffer.get_selection_bounds()
        if limites:
            debut, fin = limites
            if action:
                buffer.remove_tag(buffer.balise_tabs_perso, debut, fin)
            else:
                buffer.apply_tag(buffer.balise_tabs_perso, debut, fin)

    def change_appliquer_couleurs(self, action, widget):
        buffer = self.zonetexte.get_buffer()
        limites = buffer.get_selection_bounds()
        if limites:
            debut, fin = limites
            if not action:
                for balise in buffer.balises_couleurs:
                    buffer.remove_tag(balise, debut, fin)
            else:
                tmp = buffer.balises_couleurs
                i = 0
                suivant = debut.copy()
                while suivant.compare(fin) < 0:
                    suivant.forward_chars(2)
                    if suivant.compare(fin) >= 0:
                        suivant = fin

                    buffer.apply_tag(tmp[i], debut, suivant)
                    i += 1
                    if i >= len(tmp):
                        i = 0
                    debut = suivant.copy()

    def retirer_balises(self, action, widget):
        buffer = self.zonetexte.get_buffer()
        limites = buffer.get_selection_bounds()
        if limites:
            debut, fin = limites
            buffer.remove_all_tags(debut, fin)

    def proprietes(self, action, widget):
        #create_prop_editor(view.zonetexte, 0)
        pass

    def fct_rappel_recherche(self, dialogue, reponse):
        if (reponse != REPONSE_AVANT and
            reponse != REPONSE_ARRIERE):
            dialogue.destroy()
            return

        debut, fin = dialogue.buffer.get_bounds()
        chaine_recherche = debut.get_text(fin)

        print "Recherche de `%s'\n" % chaine_recherche

        buffer = self.zonetexte.get_buffer()
        if reponse == REPONSE_AVANT:
            buffer.recherche_avant(chaine_recherche, self)
        elif reponse == REPONSE_ARRIERE:
            buffer.recherche_arriere(chaine_recherche, self)

        dialogue.destroy()

    def rechercher(self, action, widget):
        recherche = gtk.TextView()
        dialogue = gtk.Dialog("Rechercher", self,
                              gtk.DIALOG_DESTROY_WITH_PARENT,
                              ("Vers l'avant", REPONSE_AVANT,
                               "Vers l'arriere", REPONSE_ARRIERE,
                              gtk.STOCK_CANCEL, gtk.RESPONSE_NONE))
        dialogue.vbox.pack_end(recherche, True, True, 0)
        dialogue.buffer = recherche.get_buffer()
        dialogue.connect("response", self.fct_rappel_recherche)

        recherche.show()
        recherche.grab_focus()
        dialogue.show_all()

    def rappel_enfants_deplace(self, enfant, evenement):
        zonetexte = self.zonetexte
        info = enfant.get_data("info-depl-testtexte")

        if not info:
            info = {}
            info['x_debut'] = -1
            info['y_debut'] = -1
            info['bouton'] = -1
            enfant.set_data("info-depl-testtexte", info)

        if evenement.type == gtk.gdk.BUTTON_PRESS:
            if info['bouton'] < 0:
                info['bouton'] = evenement.button
                info['x_debut'] = enfant.allocation.x
                info['y_debut'] = enfant.allocation.y
                info['x_clic'] = enfant.allocation.x + evenement.x
                info['y_clic'] = enfant.allocation.y + evenement.y
        elif evenement.type == gtk.gdk.BUTTON_RELEASE:
            if info['bouton'] < 0:
                return False

            if info['bouton'] == evenement.button:
                info['bouton'] = -1;
                # conversion coordonnees event box --> coordonnes fenetre
                x = info['x_debut'] + (evenement.x + enfant.allocation.x \
                                       - info['x_clic'])
                y = info['y_debut'] + (evenement.y + enfant.allocation.y \
                                       - info['y_clic'])
                zonetexte.move_child(enfant, x, y)
        elif gtk.gdk.MOTION_NOTIFY:
            if info['bouton'] < 0:
                return False
            x, y = enfant.get_pointer() # ensure more events
            # coordonnees event box --> coordonnes fenetres
            x += enfant.allocation.x
            y += enfant.allocation.y
            x = info['x_debut'] + (x - info['x_clic'])
            y = info['y_debut'] + (y - info['y_clic'])
            zonetexte.move_child(enfant, x, y)

        return False

    def ajouter_enfants_deplace(self, zonetexte, fenetre):
        etiquette = gtk.Label("Deplacez-moi")

        boite_evnmt = gtk.EventBox()
        boite_evnmt.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                             gtk.gdk.BUTTON_RELEASE_MASK |
                             gtk.gdk.POINTER_MOTION_MASK |
                             gtk.gdk.POINTER_MOTION_HINT_MASK)

        couleur = TestTexte.tabledescouleurs.alloc_color(0xffff, 0, 0)
        boite_evnmt.modify_bg(gtk.STATE_NORMAL, couleur)
        boite_evnmt.add(etiquette)
        boite_evnmt.show_all()

        boite_evnmt.connect("event", self.rappel_enfants_deplace)

        zonetexte.add_child_in_window(boite_evnmt, fenetre, 0, 0)

    def ajouter_enfants(self, action, widget):
        zonetexte = self.zonetexte
        self.ajouter_enfants_deplace(zonetexte, gtk.TEXT_WINDOW_WIDGET)
        self.ajouter_enfants_deplace(zonetexte, gtk.TEXT_WINDOW_LEFT)
        self.ajouter_enfants_deplace(zonetexte, gtk.TEXT_WINDOW_RIGHT)
        self.ajouter_enfants_deplace(zonetexte, gtk.TEXT_WINDOW_TEXT)
        self.ajouter_enfants_deplace(zonetexte, gtk.TEXT_WINDOW_TOP)
        self.ajouter_enfants_deplace(zonetexte, gtk.TEXT_WINDOW_BOTTOM)

    def ajouter_enfants_focus(self, action, widget):
        zonetexte = self.zonetexte

        enfant = gtk.EventBox()
        b = gtk.Button("Bouton _A dans fenetre du widget")
        enfant.add(b)
        zonetexte.add_child_in_window(enfant, gtk.TEXT_WINDOW_WIDGET, 0, 200)

        enfant = gtk.EventBox()
        b = gtk.Button("Bouton _B dans fenetre du texte")
        enfant.add(b)
        zonetexte.add_child_in_window(enfant, gtk.TEXT_WINDOW_TEXT, 50, 50)

        enfant = gtk.EventBox()
        b = gtk.Button("Bouton _T dans fenetre superieure")
        enfant.add(b)
        zonetexte.add_child_in_window(enfant, gtk.TEXT_WINDOW_TOP, 100, 0)

        enfant = gtk.EventBox()
        b = gtk.Button("Bouton _W dans fenetre inferieure")
        enfant.add(b)
        zonetexte.add_child_in_window(enfant, gtk.TEXT_WINDOW_BOTTOM, 100, 0)

        enfant = gtk.EventBox()
        b = gtk.Button("Bouton _C dans fenetre gauche")
        enfant.add(b)
        zonetexte.add_child_in_window(enfant, gtk.TEXT_WINDOW_LEFT, 0, 50)

        enfant = gtk.EventBox()
        b = gtk.Button("Bouton _D dans fenetre droite")
        enfant.add(b)
        zonetexte.add_child_in_window(enfant, gtk.TEXT_WINDOW_RIGHT, 0, 25)

        buffer = zonetexte.get_buffer()
        iter = buffer.get_start_iter()
        ancrage = buffer.create_child_anchor(iter)
        enfant = gtk.Button("Bouton _E dans buffer")
        zonetexte.add_child_at_anchor(enfant, ancrage)

        ancrage = buffer.create_child_anchor(iter)
        enfant = gtk.Button("Bouton _F dans buffer")
        zonetexte.add_child_at_anchor(enfant, ancrage)

        ancrage = buffer.create_child_anchor(iter)
        enfant = gtk.Button("Bouton _G dans buffer")
        zonetexte.add_child_at_anchor(enfant, ancrage)

        # On affiche tous les boutons
        zonetexte.show_all()

    def init_menus(self):
        zonetexte = self.zonetexte
        direction = zonetexte.get_direction()
        retour_ligne = zonetexte.get_wrap_mode()
        commande = None

        if direction == gtk.TEXT_DIR_LTR:
            commande = self.barremenus.get_widget("/Options/De gauche a droite")
        elif direction == gtk.TEXT_DIR_RTL:
            commande = self.barremenus.get_widget("/Options/De droite a gauche")

        if commande:
            commande.activate()

        if retour_ligne == gtk.WRAP_NONE:
            commande = self.barremenus.get_widget("/Options/Pas de retour a la ligne auto")
        elif direction == gtk.WRAP_WORD:
            commande = self.barremenus.get_widget("/Options/Retour a la ligne apres mot")
        elif direction == gtk.WRAP_CHAR:
            commande = self.barremenus.get_widget("/Options/Retour a la ligne apres caractere")

        if commande:
            commande.activate()

    def fermer_fenetre(self):
        TestTexte.fenetres.remove(self)
        buffer = self.zonetexte.get_buffer()
        buffer.decr_comptref()
        buffer.disconnect(self.bhid)
        self.zonetexte.destroy()
        del self.zonetexte
        self.zonetexte = None
        self.destroy()
        del self
        if not TestTexte.fenetres:
            gtk.main_quit()

    def verif_fermer_fenetre(self):
        buffer = self.zonetexte.get_buffer()
        if (buffer.comptref > 1 or
            buffer.verif_buffer_enreg()):
            self.fermer_fenetre()

    def titre_fenetre(self):
        nom_simple = self.zonetexte.get_buffer().nom_simple()
        titre = "testtexte - " + nom_simple
        self.set_title(titre)

    def rappel_mvt_curseur(self, buffer, emplacement, marque):
        # On redessine les fenetres contenant les traits de tabulation
        # quand le curseur se deplace dans la fenetre du widget (les
        # fenetres peuvent ne pas exister avant la realisation...)
        zonetexte = self.zonetexte
        if marque == buffer.get_insert():
            fenetre_tab = zonetexte.get_window(gtk.TEXT_WINDOW_TOP)
            fenetre_tab.invalidate_rect(None, False)
            #fenetre_tab.invalidate_rect(fenetre_tab.get_geometry()[:4], False)

            fenetre_tab = zonetexte.get_window(gtk.TEXT_WINDOW_BOTTOM)
            fenetre_tab.invalidate_rect(None, False)
            #fenetre_tab.invalidate_rect(fenetre_tab.get_geometry()[:4], False)

    def reaffichage_tabs(self, widget, evenement):
        #print self, widget, evenement
        zonetexte = widget

        # On controle si l'evenement vient des fenetres avec tabulations
        fenetre_sup = zonetexte.get_window(gtk.TEXT_WINDOW_TOP)
        fenetre_inf = zonetexte.get_window(gtk.TEXT_WINDOW_BOTTOM)

        if evenement.window == fenetre_sup:
            type = gtk.TEXT_WINDOW_TOP
            cible = fenetre_sup
        elif evenement.window == fenetre_inf:
            type = gtk.TEXT_WINDOW_BOTTOM
            cible = fenetre_inf
        else:
            return False

        premier_x = evenement.area.x
        dernier_x = premier_x + evenement.area.width

        premier_x, y = zonetexte.window_to_buffer_coords(type, premier_x, 0)
        dernier_x, y = zonetexte.window_to_buffer_coords(type, dernier_x, 0)

        buffer = zonetexte.get_buffer()
        curseur = buffer.get_iter_at_mark(buffer.get_insert())
        attrs = gtk.TextAttributes()
        curseur.get_attributes(attrs)

        listetabs = []
        en_pixels = False
        if attrs.tabs:
            listetabs = attrs.tabs.get_tabs()
            en_pixels = attrs.tabs.get_positions_in_pixels()

        for align, position in listetabs:
            if not en_pixels:
                position = pango.PIXELS(position)

            pos, y = zonetexte.buffer_to_window_coords(type, position, 0)
            cible.draw_line(zonetexte.style.fg_gc[zonetexte.state],
                             pos, 0, pos, 15)

        return True

    def recup_lignes(self, premier_y, dernier_y, coords_buffer, numeros):
        zonetexte = self.zonetexte
        # On recupere l'iterateur du premier y.
        iter, top = zonetexte.get_line_at_y(premier_y)

        # On recupere la position de chaque iterateur et on l'ajoute
        # a la liste. On s'arrete apres dernier_y.
        nombre = 0
        taille = 0

        while not iter.is_end():
            y, hauteur = zonetexte.get_line_yrange(iter)
            coords_buffer.append(y)
            num_ligne = iter.get_line()
            numeros.append(num_ligne)
            nombre += 1
            if (y + hauteur) >= dernier_y:
                break
            iter.forward_line()

        return nombre

    def affichage_num_lignes(self, widget, evenement, donnees=None):
        zonetexte = widget

        # On controle si l'evenement vient de la fenetre des numeros de ligne
        fenetre_gauche = zonetexte.get_window(gtk.TEXT_WINDOW_LEFT)
        fenetre_droite = zonetexte.get_window(gtk.TEXT_WINDOW_RIGHT)

        if evenement.window == fenetre_gauche:
            type = gtk.TEXT_WINDOW_LEFT
            cible = fenetre_gauche
        elif evenement.window == fenetre_droite:
            type = gtk.TEXT_WINDOW_RIGHT
            cible = fenetre_droite
        else:
            return False

        premier_y = evenement.area.y
        dernier_y = premier_y + evenement.area.height

        x, premier_y = zonetexte.window_to_buffer_coords(type, 0, premier_y)
        x, dernier_y = zonetexte.window_to_buffer_coords(type, 0, dernier_y)

        numeros = []
        pixels = []
        nombre = self.recup_lignes(premier_y, dernier_y, pixels, numeros)

        # Affichage de numeros totalement internationalises !
        positionnement = widget.create_pango_layout("")

        for i in range(nombre):
            x, pos = zonetexte.buffer_to_window_coords(type, 0, pixels[i])
            chaine = "%d" % numeros[i]
            positionnement.set_text(chaine)
            widget.style.paint_layout(cible, widget.state, False,
                                      None, widget, None, 2, pos + 2, positionnement)

        # l'evenement doit continuer a etre emis, il faut reafficher les enfants
        return False

    def ajouter_widgets_exemples(self):
        buffer = self.zonetexte.get_buffer()

        ancrage = buffer.get_data("ancrage")

        if (ancrage and not ancrage.get_deleted()):
            widget = gtk.Button("Tadam !")
            self.zonetexte.add_child_at_anchor(widget, ancrage)
            widget.show()

class Pile(list):
    def __init__(self):
        list.__init__(self)

    def empiler(self, element):
        self.insert(-1, element)

    def depiler(self):
        del self[0]

    def recuperer(self):
        return self[0]

class TestTexte:
    sanstitre_num = 1
    tabledescouleurs = None
    pile_fenetre_active = Pile()
    buffers = Pile()
    fenetres = Pile()

    def __init__(self, listefichiers):
        fenetre = Fenetre()
        self.pile_fenetre_active.empiler(fenetre)
        for fichier in listefichiers:
            nomfichier = os.path.abspath(fichier)
            fenetre.ouvrir_ok(nomfichier)
        self.pile_fenetre_active.depiler()

    def main(self):
        gtk.main()
        return 0

if __name__ == "__main__":
    testtexte = TestTexte(sys.argv[1:])
    testtexte.main()
