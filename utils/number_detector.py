import math
import re

from utils.common_regexes import (ALL_NUMBERS, INTEGER_NUMBERS)
from utils.pre_processing import turkish_lower


class NumberDetector(object):
    SEPARATORS = r"[ ;:]"

    NUMBER_SEARCH_REGEX = re.compile(r'(^|{}+)({}(?: {})*)(?:{}+|$)'
                                     .format(SEPARATORS, ALL_NUMBERS, ALL_NUMBERS, SEPARATORS), re.IGNORECASE)

    INT_NUMBERS_REGEX = re.compile(INTEGER_NUMBERS)

    TEXT_NUMBER_MAP = {'sıfır': 0, 'bir': 1, 'iki': 2, 'üç': 3, 'dört': 4, 'beş': 5, 'altı': 6, 'yedi': 7, 'sekiz': 8,
                       'dokuz': 9, 'on': 10, 'yirmi': 20, 'otuz': 30, 'kırk': 40, 'elli': 50, 'altmış': 60,
                       'yetmiş': 70, 'seksen': 80, 'doksan': 90, 'yüz': 100, 'bin': 1000, 'milyon': 1000000,
                       'milyar': 1000000000, 'trilyon': 1000000000000, 'katrilyon': 1e15}

    @staticmethod
    def _get_value(numbers):
        """ Calculate the overall value of a given list of numbers.

        Numbers in string form can seem disconnected. From a dumb standpoint the expression
        "two hundred" can mean separately "2" and "100" as opposed to the intended "200" value.

        This function takes, for example, ["2", "100"] and returns "200".
        """
        res = 0
        i = len(numbers) - 1
        current_bin = 0  # bins -> 1e0, 1e3, 1e6...

        while i >= 0:
            if numbers[i] % 1000 == 0:
                # Make sure that bin is strictly increasing
                current_bin = len(str(numbers[i])) - 1

                # Find the associated value
                j = i - 1
                temp_res = 0
                while j >= 0 and numbers[j] % 100 != 0:
                    temp_res += numbers[j]
                    j -= 1

                if temp_res != 0:  # Found a value
                    res += temp_res * numbers[i]
                    i = j + 1
                else:  # No value found
                    if i == 0 or numbers[i - 1] % 100 != 0:
                        res += numbers[i]
            elif numbers[i] % 100 == 0:
                # Find the value associated with 100 (its either in front with value [1-9] or there is none)
                if i > 0 and numbers[i - 1] % 100 != 0:
                    res += numbers[i - 1] * 100 * math.pow(10, current_bin)
                    i -= 1
                else:
                    res += numbers[i] * math.pow(10, current_bin)
            else:
                res += numbers[i]

            i -= 1
        return res

    def convert2number(self, text):
        """ Extract the numerical value of a text.
        """
        text = text.replace('.', '')
        text = turkish_lower(text)

        # Recursively handle fractions
        if ',' in text:
            splits = text.split(',')
            fraction = float(self.convert2number(''.join(splits[1:]))) / math.pow(10, len(''.join(splits[1:])))
            return float(self.convert2number(splits[0])) + fraction

        number_list = []
        int_number_cache = ''
        token = ''
        for ch in text:
            token += ch

            if self.INT_NUMBERS_REGEX.match(token.strip()):
                int_number_cache += token.strip()
                token = ''
            elif token.strip() in self.TEXT_NUMBER_MAP:
                number_list.append(self.TEXT_NUMBER_MAP[token.strip()])
                token = ''
            elif len(int_number_cache) > 0:
                number_list.append(int(int_number_cache))
                int_number_cache = ''
                token = ''

        if len(int_number_cache) > 0:
            number_list.append(int(int_number_cache))

        return self._get_value(number_list)

    def find_all(self, text):
        found_numbers = []
        for match in re.finditer(self.NUMBER_SEARCH_REGEX, text):
            offset_ = match.start() + len(match.group(1))
            match_text = match.group(2)  # Group 2 doesn't include separators surrounding the expression
            found_numbers.append({
                'type': 'number',
                'start_index': + offset_,
                'end_index': offset_ + len(match_text),
                'text': match_text,
                'value': self.convert2number(match_text)
            })
        return found_numbers
