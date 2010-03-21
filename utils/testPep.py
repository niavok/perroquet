#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import pep8

class Pep8FunctionsTestCase(unittest.TestCase):
    def test_set_lower(self):
        self.assertEqual(pep8.set_loweru("aZzzE"), "a_zzz_e")
        self.assertEqual(pep8.set_loweru("t_tt"), "t_tt")
        self.assertEqual(pep8.set_loweru("a_ZzzE"), "a_zzz_e")
        self.assertEqual(pep8.set_loweru("TestOne"), "test_one")
    
    def test_find_functions_names(self):
        text="""
        def test_affd():
            pass
            
        def test_bddr():
            pass
        
        def test_ee():
            pass
        """
        self.assertEqual(pep8.find_function_names(text),
                        ["test_affd", "test_bddr"])
        
    def test_replace_word(self):
        text = "test a.test test.b a.test.a rrtestrr r_test_a"
        text_ = "TEST 1.TEST TEST.b 1.TEST.1 rrtestrr r_test_a"
        tuples = [("test", "TEST"), ("a", "1")]
        self.assertEqual(pep8.replace_words(tuples, text), text_)
        
class Pep8FunctionsBlank(unittest.TestCase):
    def test_rm_blanks(self):
        text1="""
        def a():
            
            pass
        """
        text1_="""
        def a():
            pass
        """
        text11="""
        def a():
            
          
          
          
            pass
        """
        self.assertEqual(pep8.set_blanks_lines(text1), text1_)
        self.assertEqual(pep8.set_blanks_lines(text11), text1_)
        text2="""
class a:
        def a():
            pass

        def b()
        """
        text22="""
class a:
        def a():
            pass
    
        
            
        def b()
        """
        text23="""
class a:
        def a():
            pass
        def b()
        """
        text2_=text2
        self.assertEqual(pep8.set_blanks_lines(text2), text2)
        self.assertEqual(pep8.set_blanks_lines(text22), text2)
        self.assertEqual(pep8.set_blanks_lines(text23), text2)
        text2="""
class a:
        def a():
            pass


class b:
        """
        text22="""
class a:
        def a():
            pass




class b:
        """
        text23="""
class a:
        def a():
            pass
class b:
        """
        text2_=text2
        self.assertEqual(pep8.set_blanks_lines(text2), text2)
        self.assertEqual(pep8.set_blanks_lines(text22), text2)
        self.assertEqual(pep8.set_blanks_lines(text23), text2)
        text3="""
def a():
    pass


def b():
        """
        text32="""
def a():
    pass





def b():
        """
        text33="""
def a():
    pass
def b():
        """
        self.assertEqual(pep8.set_blanks_lines(text3), text3)
        self.assertEqual(pep8.set_blanks_lines(text32), text3)
        self.assertEqual(pep8.set_blanks_lines(text33), text3)
        text=""" "a new class" """
        text2= '   """A general class to make parsers""" '
        self.assertEqual(pep8.set_blanks_lines(text), text)
        self.assertEqual(pep8.set_blanks_lines(text2), text2)
        
    
if __name__=="__main__":
    unittest.main()
