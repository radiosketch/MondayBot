import sys
import unittest
import logging
import utils

from dateutil import parser

logger = logging.getLogger()
logger.level = logging.DEBUG

class DateMethods(unittest.TestCase):
    
    def test_generate_next_joke_monday(self):
        joke_monday, i = utils.generate_next_joke_monday()
        logger.debug(f'The next ({utils.ordinal(i)}) joke monday is {joke_monday}')

    def test_generate_next_real_monday(self):
        next_monday, _ = utils.generate_next_real_monday(parser.parse('September 28th, 2023'))
        self.assertEqual(next_monday, parser.parse('October 2nd, 2023'))

    def test_generate_next_super_monday(self):
        next_super_monday = utils.generate_next_super_monday()

    def test_today_is_real_monday(self):
        is_real_monday = utils.is_real_monday()
        logger.debug(f'Today {"is" if is_real_monday else "is not"} a real Monday')
    
    def test_today_is_joke_monday(self):
        is_joke_monday = utils.is_joke_monday()
        logger.debug(f'Today {"is" if is_joke_monday else "is not"} a joke Monday')
    
    def test_today_is_super_monday(self):
        is_super_monday = utils.is_super_monday()
        logger.debug(f'Today {"is" if is_super_monday else "is not"} a super Monday')

    def test_true_is_real_monday(self):
        is_real_monday = utils.is_real_monday(day=parser.parse('October 2nd, 2023'))
        self.assertTrue(is_real_monday)

    def test_true_is_joke_monday(self):
        is_joke_monday = utils.is_joke_monday(day=parser.parse('October 19th, 2023'))
        self.assertTrue(is_joke_monday)

    def test_true_is_super_monday(self):
        is_super_monday = utils.is_super_monday(day=parser.parse('June 3rd, 2024'))
        self.assertTrue(is_super_monday)

if __name__ == '__main__':
    unittest.main()