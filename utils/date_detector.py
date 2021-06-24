import re
from calendar import monthrange
from datetime import timedelta, date, datetime

import dateparser

from utils.common_regexes import (CASE_SUFFIXES, GENITIVE_SUFFIXES,
                                  NATURAL_NUMBERS, CONJUNCTIONS, PRONOUN_SUFFIX, PLURALITY_SUFFIXES,
                                  POSSESSIVE_SUFFIXES)
from utils.number_detector import NumberDetector
from utils.pre_processing import turkish_lower


def date_creator(year=None, month=None, day=None, hour=None, minute=None, second=None,
                 dyear=None, dmonth=None, dday=None, dhour=None, dminute=None, dsecond=None,
                 dweek=None, round_year=False, week_day=None, month_str=None):
    """
    A higher order function for creating date objects. Regex matched groups are parsed by the
    inner function, `regex_group_helper`.
    """
    day_offset_map = {
        "pazartesi": 0, "salı": 1, "çarşamba": 2, "perşembe": 3, "cuma": 4, "cumartesi": 5, "pazar": 6
    }

    num_to_month_map = {
        1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
        7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım", 12: "aralık"
    }
    month_to_num_map = {month: num for num, month in num_to_month_map.items()}

    def regex_group_helper(rule_regex, input_expr):
        def parse_value(val, default=0, value_map=None):
            """
            Helper method for evaluating group values
            """
            if val is None:
                return default
            elif isinstance(val, str):
                group_val = re.sub(rule_regex, val, input_expr)
                if not value_map:
                    return int(group_val)
                else:
                    return int(value_map[group_val])
            else:
                return val

        year_val = parse_value(year, default=date.today().year)
        month_val = parse_value(month_str, default=date.today().month, value_map=month_to_num_map)
        if not month_str:
            month_val = parse_value(month, default=date.today().month)

        if round_year and (date.today().month < month_val):
            year_val -= 1

        if dyear:
            year_val += parse_value(dyear)

        if dmonth:
            d_month_val = parse_value(dmonth)
            year_val += int(d_month_val / 12)
            if d_month_val < 0:
                month_val -= abs(d_month_val) % 12
            else:
                month_val += d_month_val % 12

            if month_val < 1:
                year_val -= 1
                month_val += 12
            elif month_val > 12:
                year_val += 1
                month_val -= 12

        if day == 'last':
            day_val = monthrange(year_val, month_val)[1]
        else:
            day_val = parse_value(day, default=date.today().day)
        hour_val = parse_value(hour, default=datetime.now().hour)
        minute_val = parse_value(minute, default=datetime.now().minute)
        second_val = parse_value(second, default=datetime.now().second)

        date_obj = datetime(year_val, month_val, day_val, hour_val, minute_val, second_val)

        if dweek:
            date_obj += timedelta(weeks=parse_value(dweek))

        if dday:
            date_obj += timedelta(days=parse_value(dday))

        if week_day is not None:
            week_day_offset = parse_value(week_day, value_map=day_offset_map) - date.today().weekday()
            date_obj += timedelta(days=week_day_offset)

        if dhour:
            date_obj += timedelta(hours=parse_value(dhour))

        if dminute:
            date_obj += timedelta(minutes=parse_value(dminute))

        if dsecond:
            date_obj += timedelta(minutes=parse_value(dsecond))

        return date_obj

    return regex_group_helper


class DateDetector(object):
    lan = 'tr'
    lan_locale = 'tr-CY'

    TYPE_DATETIME = "datetime"
    TYPE_DATESPAN = "date-span"
    TYPE_PERIOD = "date-period"
    SPAN_SEPARATOR = "\t"

    number_detector = NumberDetector()

    # Span identifying words
    SPAN_IMPLYING = r"(?:(?:boyunca)|(?:süresince)|(?:arası(?:nda)?)|(?:içeri?sinde)|(?:içinde))"
    # relative date expressions
    BEFORE_EXPRESSION = r"(?:(?:geçen(?:ki)?)|(?:önce(?:[sk]i)?)|(?:evvel(?:[sk]i)?)|(?:geçtiğimiz)|(?:diğer)|(?:son))"
    FIRST_EXPRESSION = r"(?:ilk|birinci|1(?:\.)?|1(?:inci)?)"
    LATER_EXPRESSION = r"(?:(?:sonra(?:[ks][iı])?)|(?:önümüzdeki)|(?:haftaya)|(?:gelecek)|(?:içinde)|(?:gelecek))"
    # minute expressions
    MINUTE_EXPRESSION = r"(?:(?:daki?ka)|dk)"
    # year expressions
    YEAR_EXPRESSION = r"(?:(?:yıl)|(?:sene))"
    # pm regexes
    PM_EXPRESSION = r"(?:(?:akşam ?üstü)|(?:öğleden sonra)|(?:akşam)|(?:akşam ?üzeri))"
    AM_EXPRESSION = r"(?:(?:öğlenden önce)|(?:sabah)|(?:gece))"
    # day expressions
    DAYS_EXPRESSION = r"(?:pazartesi)|(?:salı)|(?:çarşamba)|(?:perşembe)|(?:cuma)|(?:cumartesi)|(?:pazar)"
    # month expressions
    MONTHS_EXPRESSION = r"(?:(?:[Oo]ca[k])|(?:[Şş]ubat)|(?:[Mm]art)|(?:[Nn]isan)|(?:[Mm]ayıs)|" \
                        r"(?:[Hh]aziran)|(?:[Tt]emmuz)|(?:[Aa]ğustos)|(?:[Ee]ylül)|(?:[Ee]kim)|" \
                        r"(?:[Kk]asım)|(?:[Aa]ralık))"
    MONTHS_ABBR_EXPRESSION = r"(?:[Oo]ca)|(?:[Şş]ub)|(?:[Mm]ar)|(?:[Nn]is)|(?:[Mm]ay)|(?:[Hh]az)|(?:[Tt]em)|" \
                             r"(?:[Aa]ğu)|(?:[Ee]yl)|(?:[Ee]ki)|(?:[Kk]as)|(?:[Aa]ra)"

    MONTH = r"(?:(?:ay(?:(?:ın)|(?:ki)|(?:a))?)|(?:dönem))"

    # week expression
    WEEK_EXPRESSION = r"hafta(?:{}|{})?".format(CASE_SUFFIXES, GENITIVE_SUFFIXES)

    DATE_SEPARATORS = r"(?:[_, \-\.\\\/])"
    YEAR_ONLY_EXPRESSION = r"(?:(?:19[0-9][0-9])|(?:20[0-2][0-9]))"
    YEAR_DD_MM_YYYY = r"(?:([0-3][0-9]){}([01][0-9]){}({}))".format(DATE_SEPARATORS, DATE_SEPARATORS,
                                                                    YEAR_ONLY_EXPRESSION),

    YEAR_ONLY_REGEX = re.compile(r"^(?:({})(?:(?:{})|(?: {}{}))?)$"
                                 .format(YEAR_ONLY_EXPRESSION, CASE_SUFFIXES, YEAR_EXPRESSION, CASE_SUFFIXES),
                                 re.UNICODE)

    """
    Holds the list of regexes a a list of tuples.
    Each tuple has the format:
    (regex_name, regex, replacement, type)
    """
    regex_list = [
        # ########### Date Times ###########
        ("NOW_REGEX", TYPE_DATETIME,
         re.compile(r"^((şuan)|(şimdi)|(hemen)|(acil)|(birazdan)|(tez( zaman)?)|(derhal)){}?$"
                    .format(CASE_SUFFIXES), re.UNICODE),
         date_creator()),

        # minute before
        ("MINUTE_BEFORE_REGEX", TYPE_DATETIME,
         re.compile(r"^([0-9]+) {}( {})$".format(MINUTE_EXPRESSION, BEFORE_EXPRESSION), re.UNICODE),
         date_creator(dminute='-\\1')),

        # minute after; ex: 1 dkye
        ("MINUTE_AFTER_REGEX", TYPE_DATETIME,
         re.compile(r"^([0-9]+) {}((y[ae])|( {}))$".format(MINUTE_EXPRESSION, LATER_EXPRESSION), re.UNICODE),
         date_creator(dminute='\\1')),

        # hour expressions; ex: 12:59
        ("HOUR_REGEX", TYPE_DATETIME,
         re.compile(r"^([012][0-9])[: ,.]([0-6][0-9])$"),
         date_creator(hour='\\1', minute='\\2')),

        # pm with hour; ex: akşamüstü 1
        ("PM_REGEX_1", TYPE_DATETIME,
         re.compile("^{} ([01]?[0-9])$".format(PM_EXPRESSION), re.UNICODE),
         date_creator(hour='\\1', dhour=12, minute=0, second=0)),

        # pm without hour # TODO 4-6 arası span
        ("PM_REGEX_2", TYPE_DATETIME,
         re.compile(r"^{}$".format(PM_EXPRESSION), re.UNICODE),
         date_creator(hour=17, minute=0, second=0)),

        # am with hour; ex: sabah 8
        ("AM_REGEX_1", TYPE_DATETIME,
         re.compile(r"^{} ([01]?[0-9])$".format(AM_EXPRESSION), re.UNICODE),
         date_creator(hour='\\1', minute=0, second=0)),

        # am without hour; ex: sabah  # TODO 4-6 arası span
        ("AM_REGEX_2", TYPE_DATETIME,
         re.compile(r"^{}$".format(AM_EXPRESSION), re.UNICODE),
         date_creator(hour=8, minute=0, second=0)),

        # 2 days later; ex: öbürsü gün # TODO span
        ("THE_DAY_AFTER_TOMORROW_REGEX", TYPE_DATETIME,
         re.compile(r"^öbür(sü)? gün$", re.UNICODE),
         date_creator(dday=2)),

        # next date; ex: önümüzdeki salı # TODO span
        ("NEXT_DATE_REGEX", TYPE_DATETIME,
         re.compile(r"^{} ({})$".format(LATER_EXPRESSION, DAYS_EXPRESSION), re.UNICODE),
         date_creator(week_day="\\1", dweek=1)),

        # preceding date; ex: geçen salı # TODO span
        ("PRECEDING_DATE_REGEX", TYPE_DATETIME,
         re.compile(r"^{} ({})$".format(BEFORE_EXPRESSION, DAYS_EXPRESSION), re.UNICODE),
         date_creator(week_day="\\1", dweek=-1)),

        # n days later; ex: 10 gün sonra
        ("LATER_DAY_REGEX", TYPE_DATETIME,
         re.compile(r"^(?:([0-9]+) (gün ((içinde)|(boyunca)|(sonra(sı(nda)?)?))))$", re.UNICODE),
         date_creator(dday="\\1")),

        # n days before; ex: 4 gün önce
        ("BEFORE_DAY_REGEX", TYPE_DATETIME,
         re.compile(r"^([0-9]+) gün {}$".format(BEFORE_EXPRESSION), re.UNICODE),
         date_creator(dday="-\\1")),

        # dd-month; 19 ağustostaki # TODO
        ("MONTH_REGEX", TYPE_DATETIME,
         re.compile(r"^([0-3]?[0-9]){}({})(?:{})$".format(DATE_SEPARATORS, MONTHS_EXPRESSION, CASE_SUFFIXES),
                    re.UNICODE),
         date_creator(month_str="\\2", day="\\1")),

        # end of month; ex: ağustos sonu, ağustos ayı sonu # TODO span
        ("EO_MONTH_REGEX", TYPE_DATETIME,
         re.compile(r"^({})(?:(?:{})|(?: ayı))? sonu(ndaki)?$".format(MONTHS_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         date_creator(month_str="\\1", day="last")),

        # start of month; ex: ekim başı # TODO span
        ("SO_MONTH_REGEX", TYPE_DATETIME,
         re.compile(r"^({})(?:{})? ((ilk günü(ndeki)?)|(başı(nda(ki)?)?))$"
                    .format(MONTHS_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         date_creator(month_str="\\1", day=1)),

        # start of this month; bu ayın ilk günü # TODO span
        ("SO_THIS_MONTH_REGEX", TYPE_DATETIME,
         re.compile(r"^(?:bu )?{} (?:(?:{} günü(?:{})?)|(?:başı(?:nda(?:ki)?)?)|(?:biri))$"
                    .format(MONTH, FIRST_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         date_creator(day=1)),

        # start of last month; ex: geçen ayın birinci günü # TODO span
        ("SO_PRECEDING_MONTH_REGEX", TYPE_DATETIME,
         re.compile(r"^{} {} (?:(?:(?:ilk|birinci) günü(?:ndeki)?)|(?:başı(?:nda(?:ki)?)?)|(?:biri))$"
                    .format(BEFORE_EXPRESSION, MONTH), re.UNICODE),
         date_creator(dmonth=-1, day=1)),

        # end of this month; ex: bu ayın sonu
        ("EO_THIS_MONTH_REGEX", TYPE_DATETIME,
         re.compile(r"^(?:bu )?{} (?:(?:sonu(?:ndaki)?)|(?:son günü))$".format(MONTH), re.UNICODE),
         date_creator(day='last')),

        # date of month; ex: ayın 16sında
        ("DATE_OF_MONTH_REGEX", TYPE_DATETIME,
         re.compile(r"^(?:bu )?{} ([0-3]?[0-9])[ '.]?{}{}$"
                    .format(MONTH, GENITIVE_SUFFIXES, CASE_SUFFIXES), re.UNICODE),
         date_creator(day='\\1')),

        # date of month; ex: geçen ayın 16sında
        ("PRECEDING_DAY_OF_MONTH_REGEX", TYPE_DATETIME,
         re.compile(r"^{} {} ([0-3]?[0-9])[ '.]?{}{}$"
                    .format(BEFORE_EXPRESSION, MONTH, GENITIVE_SUFFIXES, CASE_SUFFIXES), re.UNICODE),
         date_creator(day='\\1', dmonth=-1)),

        # n weeks later at a precise day, ex: 2 hafta sonra pazartesi
        ("N_WEEKS_LATER_AT_DAY", TYPE_DATETIME,
         re.compile(r"^([0-9]+) {} {} ({})$".format(WEEK_EXPRESSION, LATER_EXPRESSION, DAYS_EXPRESSION), re.UNICODE),
         date_creator(dweek='\\1', week_day='\\2')),

        # ex: 3 hafta önce pazartesi
        ("N_WEEKS_BEFORE_AT_DAY", TYPE_DATETIME,
         re.compile(r"^([0-9]+) {} {} ({})$".format(WEEK_EXPRESSION, BEFORE_EXPRESSION, DAYS_EXPRESSION), re.UNICODE),
         date_creator(dweek='-\\1', week_day='\\2')),

        # day month year; ex: 19 ocak 2005 teki TODO span
        ("DAY_MONTH_YEAR_REGEX", TYPE_DATETIME,
         re.compile(r"^([0-3]?[0-9]) ({}) ({}){}?$"
                    .format(MONTHS_EXPRESSION, YEAR_ONLY_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         date_creator(day='\\1', month_str='\\2', year='\\3')),

        # month year; ex: ocak 2005 teki TODO span
        ("MONTH_YEAR_REGEX", TYPE_DATETIME,
         re.compile(r"^({}) ({}){}?$"
                    .format(MONTHS_EXPRESSION, YEAR_ONLY_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         date_creator(month_str='\\1', year='\\2')),

        # ########### Date Spans ##########
        # today
        ("TODAY_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:bu ?gün(?:{})?)|(?:gün (?:{})))$".format(PRONOUN_SUFFIX, SPAN_IMPLYING), re.UNICODE),
         [date_creator(hour=0, minute=0, second=0), date_creator(hour=23, minute=59, second=59)]),

        # yesterday
        ("YESTERDAY_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:dün(?:{})?)|(?:{} gün))$".format(PRONOUN_SUFFIX, BEFORE_EXPRESSION), re.UNICODE),
         [date_creator(dday=-1, hour=0, minute=0, second=0), date_creator(dday=-1, hour=23, minute=59, second=59)]),

        # TODO tomorrow

        # New years; ex: yılbaşında, yıl başında, yılbaşı
        ("NEW_YEARS", TYPE_DATESPAN,
         re.compile(r"^yıl ?ba[sş][iı](?:{})?$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=1, day=1, hour=0, minute=0, second=0),
          date_creator(month=1, day=1, hour=23, minute=59, second=59)]),

        # Valentines day; sevgililer günü
        ("VALENTINES_DAY", TYPE_DATESPAN,
         re.compile(r"^sevgililer g[uü]n[uü](?:{})?$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=2, day=14, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=2, day=14, hour=23, minute=59, second=59, round_year=True)]),

        # Cumhuriyet bayramında
        ("CUMHURIYET_BAYRAMI", TYPE_DATESPAN,
         re.compile(r"^cumhuriyet bayram[iı](?:{})?$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=10, day=29, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=10, day=29, hour=23, minute=59, second=59, round_year=True)]),

        # çocuk bayramında
        ("COCUK_BAYRAMI", TYPE_DATESPAN,
         re.compile(r"^[çc]ocuk (?:(?:bayram[iı])|(?:[şs]enli[ğg]i))(?:{})?$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=4, day=23, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=4, day=23, hour=23, minute=59, second=59, round_year=True)]),

        # may day, international workers day, labour Day
        ("LABOUR_DAY", TYPE_DATESPAN,
         re.compile(r"^i[şs][çc]i bayram[iı](?:{})?$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=5, day=1, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=5, day=1, hour=23, minute=59, second=59, round_year=True)]),

        # this week
        ("THIS_WEEK_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:bu hafta(?:{})?)$".format(PRONOUN_SUFFIX), re.UNICODE),
         [date_creator(week_day=0, hour=0, minute=0, second=0), date_creator()]),

        # last week; ex: geçen hafta
        ("LAST_WEEK_REGEX", TYPE_DATESPAN,
         re.compile(r"^{} {}$".format(BEFORE_EXPRESSION, WEEK_EXPRESSION), re.UNICODE),
         [date_creator(dweek=-1, week_day=0), date_creator(dweek=-1, week_day=6)]),

        # last n weeks; ex: son 3 hafta
        ("LAST_N_WEEKS_REGEX", TYPE_DATESPAN,
         re.compile(r"^{} ({}) {}$".format(BEFORE_EXPRESSION, NATURAL_NUMBERS, WEEK_EXPRESSION), re.UNICODE),
         [date_creator(dweek='-\\1'), date_creator()]),

        # last n gün; ex: son 3 gün içinde
        ("LAST_N_DAYS_REGEX", TYPE_DATESPAN,
         re.compile(r"^{} ({}) gün(?:(?:{})|(?: {}))?$".format(BEFORE_EXPRESSION, NATURAL_NUMBERS,
                                                               PRONOUN_SUFFIX, SPAN_IMPLYING), re.UNICODE),
         [date_creator(dday='-\\1'), date_creator()]),

        # weekday
        ("WEEKDAY_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:bu )?hafta ?içi(?:{})?)$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(week_day=0, hour=0, minute=0, second=0),
          date_creator(week_day=4, hour=23, minute=59, second=59)]),

        # weekend
        ("WEEKEND_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:{} )?hafta ?sonu(?:{})?)$".format(BEFORE_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         [date_creator(dweek=-1, week_day=5, hour=0, minute=0, second=0),
          date_creator(dweek=-1, week_day=6, hour=23, minute=59, second=59)]),

        # this year; ex: bu yıl, du yıldaki
        ("THIS_YEAR_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:bu {}(?:{})?)$".format(YEAR_EXPRESSION, PRONOUN_SUFFIX), re.UNICODE),
         [date_creator(month=1, day=1, hour=0, minute=0, second=0), date_creator()]),

        # last year; ex: geçen yılki, 1 sene öncesi, son bir yılki
        ("LAST_YEAR_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:{}(?: 0*1)? {}(?:{}|{})?)|(?:0*1 {} {}))$"
                    .format(BEFORE_EXPRESSION, YEAR_EXPRESSION, CASE_SUFFIXES, PRONOUN_SUFFIX,
                            YEAR_EXPRESSION, BEFORE_EXPRESSION), re.UNICODE),
         [date_creator(dyear=-1, hour=0, minute=0, second=0), date_creator()]),

        # ex: geçen yıl eylül ayında
        ("LAST_YEAR_MONTH_REGEX", TYPE_DATESPAN,
         re.compile(r"^{} {} ({}) ayında$".format(BEFORE_EXPRESSION, YEAR_EXPRESSION, MONTHS_EXPRESSION), re.UNICODE),
         [date_creator(dyear=-1, month_str='\\1', day=1, hour=0, minute=0, second=0),
          date_creator(dyear=-1, month_str='\\1', day='last', hour=23, minute=59, second=59)]),

        # one year later; ex: 1 yıl sonra, seneye kadar, 1 yıla kadar, önümüzdeki sene, gelecek yıl
        ("ONE_YEAR_LATER_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:((bir)|(0*1)) {}({})?)( kadar)?( sonra([sk][ıi])?)?)|(?:(?:{} {}({})?)|(?:seneye))$"
                    .format(YEAR_EXPRESSION, CASE_SUFFIXES, LATER_EXPRESSION, YEAR_EXPRESSION, CASE_SUFFIXES),
                    re.UNICODE),
         [date_creator(), date_creator(dyear=1)]),

        ("N_YEAR_BEFORE_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:({}) {}({})? {})$"
                    .format(NATURAL_NUMBERS, YEAR_EXPRESSION, CASE_SUFFIXES, BEFORE_EXPRESSION), re.UNICODE),
         [date_creator(dyear='-\\1', hour=0, minute=0, second=0), date_creator()]),

        # this month
        ("THIS_MONTH_REGEX", TYPE_DATESPAN,
         re.compile(r"^bu {}(?: {})?$".format(MONTH, SPAN_IMPLYING), re.UNICODE),
         [date_creator(day=1, hour=0, minute=0, second=0), date_creator()]),

        # next month; ex: gelecek ay
        ("NEXT_MONTH_REGEX", TYPE_DATESPAN,
         re.compile(r"^{} {}({})?$".format(LATER_EXPRESSION, MONTH, CASE_SUFFIXES), re.UNICODE),
         [date_creator(dmonth=1, day=1, hour=0, minute=0, second=0),
          date_creator(dmonth=1, day='last', hour=23, minute=59, second=59)]),

        # preceding month; ex: geçtiğimiz ay
        ("PRECEDING_MONTH_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:{} {}({})?)|(?:geçenlerde))?$"
                    .format(BEFORE_EXPRESSION, MONTH, CASE_SUFFIXES), re.UNICODE),
         [date_creator(dmonth=-1, day=1, hour=0, minute=0, second=0),
          date_creator(dmonth=-1, day='last', hour=23, minute=59, second=59)]),

        # N months before; ex: 1 ay önce, iki ay önce
        ("N_MONTHS_BEFORE_REGEX", TYPE_DATESPAN,
         re.compile(r"^({}) {} {}$".format(NATURAL_NUMBERS, MONTH, BEFORE_EXPRESSION), re.UNICODE),
         [date_creator(dmonth='-\\1', day=1, hour=0, minute=0, second=0),
          date_creator(dmonth='-\\1', day='last', hour=23, minute=59, second=59)]),

        # last n months; ex: son altı ay
        ("LAST_N_MONTHS_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:{} ([01]?[0-9]) {}(?:{})?(?: {})?)$"
                    .format(BEFORE_EXPRESSION, MONTH, CASE_SUFFIXES, SPAN_IMPLYING), re.UNICODE),
         [date_creator(dmonth='-\\1', day=1, hour=0, minute=0, second=0), date_creator()]),

        # eylül ayında
        ("IN_THE_MONTH", TYPE_DATESPAN,
         re.compile(r"^(?:({}) {}(?:{})?)$".format(MONTHS_EXPRESSION, MONTH, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month_str='\\1', day=1, hour=0, minute=0, second=0),
          date_creator(month_str='\\1', day='last', hour=23, minute=59, second=59)]),

        # month + suffix; ex: ocak, ocakta
        ("JUST_MONTH", TYPE_DATESPAN,
         re.compile(r"^(?:({})(?:{})?)$".format(MONTHS_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month_str='\\1', day=1, hour=0, minute=0, second=0),
          date_creator(month_str='\\1', day='last', hour=23, minute=59, second=59)]),

        # from month till today; ex: ocaktan beri
        ("START_FROM_MONTH", TYPE_DATESPAN,
         re.compile(r"^({})(?:{})? (?:(?:{}{})|(?:tarihinden) )?(?:(?:bu(?:güne)|(?: yana))|(?:beri)|(?:sonra))$"
                    .format(MONTHS_EXPRESSION, CASE_SUFFIXES, MONTH, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month_str='\\1', day=1, hour=0, minute=0, second=0, round_year=True), date_creator()]),

        # from month till today; ex: 12 aralıktan beri
        ("START_FROM_DM", TYPE_DATESPAN,
         re.compile(r"^([1-3][0-9]) ({})(?:{})? "
                    r"(?:(?:{}{})|(?:tarihinden) )?(?:(?:bu(?:güne)|(?: yana))|(?:beri)|(?:sonra))$"
                    .format(MONTHS_EXPRESSION, CASE_SUFFIXES, MONTH, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month_str='\\2', day='\\1', hour=0, minute=0, second=0, round_year=True), date_creator()]),

        # from last month to today; geçen aydan bugüne
        ("LAST_MONTH_TODAY_REGEX", TYPE_DATESPAN,
         re.compile(r"^{} {}({})? bu((güne)|( yana))$".format(BEFORE_EXPRESSION, MONTH, CASE_SUFFIXES), re.UNICODE),
         [date_creator(dmonth=-1, day=1, hour=0, minute=0, second=0), date_creator()]),

        # between two months; ex: mayıs ve temmuz arasında
        ("BETWEEN_TWO_MONTHS_REGEX", TYPE_DATESPAN,
         re.compile(rf"^({MONTHS_EXPRESSION}){CONJUNCTIONS}({MONTHS_EXPRESSION})(?: {MONTH}(?:{PLURALITY_SUFFIXES})?"
                    rf"(?:{POSSESSIVE_SUFFIXES}|{CASE_SUFFIXES})?)? {SPAN_IMPLYING}$", re.UNICODE),
         [date_creator(month_str='\\1', day=1, hour=0, minute=0, second=0),
          date_creator(month_str='\\2', day='last', hour=23, minute=59, second=59)]),

        # from day month to day month; ex: 10 Ocak ile 12 Mayıs arasında
        ("FROM_DM_TO_DM_REGEX", TYPE_DATESPAN,
         re.compile(r"^([0-3]?[0-9]) ({})(?:{}|{})([0-3]?[0-9]) ({})(?: tarihleri)? arası(?:{})?$"
                    .format(MONTHS_EXPRESSION, DATE_SEPARATORS, CONJUNCTIONS, MONTHS_EXPRESSION,
                            CASE_SUFFIXES), re.UNICODE),
         [date_creator(month_str='\\2', day='\\1', hour=0, minute=0, second=0),
          date_creator(month_str='\\4', day='\\3', hour=23, minute=59, second=59)]),

        # dd-mm-yyyy dd-mm-yyyy # TODO test this
        ("FROM_TO_DATE_SPAN_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:{})(?:{}|{})?(?:{})(?: (?:tarihleri)? arası(?:{})?)?$"
                    .format(YEAR_DD_MM_YYYY, DATE_SEPARATORS, CONJUNCTIONS, YEAR_DD_MM_YYYY, CASE_SUFFIXES),
                    re.UNICODE),
         [date_creator(year='\\3', month='\\2', day='\\1', hour=0, minute=0, second=0),
          date_creator(year='\\6', month='\\5', day='\\4', hour=23, minute=59, second=59)]),

        # from day month year to day month year; ex: 12 aralık 2017 ve 13 ocak 2018 arasında
        ("FROM_DMY_TO_DMY_REGEX", TYPE_DATESPAN,
         re.compile(r"^([0-3]?[0-9]) ({}) ({})(?:{}|{})([0-3]?[0-9]) ({}) ({})(?: tarihleri)? arası(?:{})?$"
                    .format(MONTHS_EXPRESSION, YEAR_ONLY_EXPRESSION, DATE_SEPARATORS, CONJUNCTIONS,
                            MONTHS_EXPRESSION, YEAR_ONLY_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         [date_creator(year='\\3', month_str='\\2', day='\\1', hour=0, minute=0, second=0),
          date_creator(year='\\6', month_str='\\5', day='\\4', hour=23, minute=59, second=59)]),

        # from day to day within month; ex: 10 15 Şubat 2017 tarihleri arasında
        ("FROM_D_TO_DMY_REGEX", TYPE_DATESPAN,
         re.compile(r"^([0-3]?[0-9])(?:{}|{}| )([0-3]?[0-9]) ({}) ({})(?: tarihleri)? arası(?:{})?$"
                    .format(DATE_SEPARATORS, CONJUNCTIONS, MONTHS_EXPRESSION, YEAR_ONLY_EXPRESSION,
                            CASE_SUFFIXES), re.UNICODE),
         [date_creator(year='\\4', month_str='\\3', day='\\1', hour=0, minute=0, second=0),
          date_creator(year='\\4', month_str='\\3', day='\\2', hour=23, minute=59, second=59)]),

        # from day to day within month; ex: 10 15 Şubat tarihleri arasında
        ("FROM_D_TO_DM_REGEX", TYPE_DATESPAN,
         re.compile(r"^([0-3]?[0-9])(?:{}|{}| )([0-3]?[0-9]) ({})(?: tarihleri)? arası(?:{})?$"
                    .format(DATE_SEPARATORS, CONJUNCTIONS, MONTHS_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month_str='\\3', day='\\1', hour=0, minute=0, second=0),
          date_creator(month_str='\\3', day='\\2', hour=23, minute=59, second=59)]),

        # DMY to DM; ex: 21 Mart 2017 ve 29 Mart arasında
        # from day month year to day month year
        ("FROM_DMY_TO_DM_REGEX", TYPE_DATESPAN,
         re.compile(r"^([0-3]?[0-9]) ({}) ({})(?:{}|{})([0-3]?[0-9]) ({})(?: tarihleri)? arası(?:{})?$"
                    .format(MONTHS_EXPRESSION, YEAR_ONLY_EXPRESSION, DATE_SEPARATORS, CONJUNCTIONS,
                            MONTHS_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         [date_creator(year='\\3', month_str='\\2', day='\\1', hour=0, minute=0, second=0),
          date_creator(year='\\3', month_str='\\5', day='\\4', hour=23, minute=59, second=59)]),

        # DM to DMY; ex: 21 Mart ve 29 Mart 2017 arasında
        # from day month year to day month year
        ("FROM_DM_TO_DMY_REGEX", TYPE_DATESPAN,
         re.compile(r"^([0-3]?[0-9]) ({})(?:{}|{})([0-3]?[0-9]) ({}) ({})(?: tarihleri)? arası(?:{})?$"
                    .format(MONTHS_EXPRESSION, DATE_SEPARATORS, CONJUNCTIONS,
                            MONTHS_EXPRESSION, YEAR_ONLY_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         [date_creator(year='\\5', month_str='\\2', day='\\1', hour=0, minute=0, second=0),
          date_creator(year='\\5', month_str='\\4', day='\\3', hour=23, minute=59, second=59)]),

        # first n months of the year; yılın ilk 3 ayı
        ("FIST_N_NONTHS_THIS_YEAR_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:bu )?{}(?:{})? ilk (1?[0-9]) {}(?:{})?$"
                    .format(YEAR_EXPRESSION, CASE_SUFFIXES, MONTH, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=1, day=1, hour=0, minute=0, second=0),
          date_creator(month='\\1', day='last', hour=23, minute=59, second=59)]),

        # last n months of the year yılın son 3 ayı
        ("LAST_N_NONTHS_THIS_YEAR_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:bu )?{}(?:{})? son ([0-9]) {}(?:{})?$"
                    .format(YEAR_EXPRESSION, CASE_SUFFIXES, MONTH, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=12, dmonth='-\\1', day=1, hour=0, minute=0, second=0),
          date_creator(month=12, day='last', hour=23, minute=59, second=59)]),

        # first week of month; ex: ocak ayının birinci haftası
        ("FIRST_WEEK_OF_MONTH", TYPE_DATESPAN,
         re.compile(r"^(?:({}) {}(?:{}) (?:ilk|birinci) {})$"
                    .format(MONTHS_EXPRESSION, MONTH, CASE_SUFFIXES, WEEK_EXPRESSION), re.UNICODE),
         [date_creator(month_str='\\1', day=1, hour=0, minute=0, second=0),
          date_creator(month_str='\\1', day=7, hour=23, minute=59, second=59)]),

        # only year ex: 2017
        ("WHOLE_YEAR_REGEX", TYPE_DATESPAN,
         YEAR_ONLY_REGEX,
         [date_creator(year='\\1', month=1, day=1, hour=0, minute=0, second=0),
          date_creator(year='\\1', month=12, day='last', hour=23, minute=59, second=59)]),

        # last n years ex: geçen 4 yılda
        ("LAST_N_YEARS_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:{} ({}) {}(?:{})?(?: {})?)$"
                    .format(BEFORE_EXPRESSION, NATURAL_NUMBERS, YEAR_EXPRESSION, CASE_SUFFIXES, SPAN_IMPLYING),
                    re.UNICODE),
         [date_creator(dyear='-\\1', hour=0, minute=0, second=0), date_creator()]),

        # last summer; ex: geçen yaz
        ("LAST_SUMMER_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:{} yaz(?:{})?)$".format(BEFORE_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=6, day=1, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=8, day='last', hour=23, minute=59, second=59, round_year=True)]),

        # this summer; ex: bu yaz
        ("THIS_SUMMER_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:bu )?yaz(?:{})?)$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=6, day=1, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=8, day='last', hour=23, minute=59, second=59, round_year=True)]),

        # last winter; ex: geçen kış
        ("LAST_WINTER_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:{} kı[şs](?:{})?)$".format(BEFORE_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=12, day=1, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=2, day='last', hour=23, minute=59, second=59, round_year=True)]),

        # this winter; ex: bu kış
        ("THIS_WINTER_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:bu )?kı[şs](?:{})?)$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=12, day=1, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=2, day='last', hour=23, minute=59, second=59, round_year=True)]),

        # last spirng; ex: geçen bahar
        ("LAST_SPRING_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:{} bahar(?:{})?)$"
                    .format(r"(?:(?:geçen(?:ki)?)|(?:önce(?:[sk]i)?)|(?:evvel(?:[sk]i)?)|(?:geçtiğimiz))",
                            CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=3, day=1, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=5, day='last', hour=23, minute=59, second=59, round_year=True)]),

        # this spring; ex: bu bahar
        ("THIS_SPRING_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:bu )?(?:ilk ?)?bahar(?:{})?)$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=3, day=1, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=5, day='last', hour=23, minute=59, second=59, round_year=True)]),

        # last autumn; ex: geçen sonbahar
        ("LAST_FALL_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:{} son ?bahar(?:{})?)$".format(BEFORE_EXPRESSION, CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=9, day=1, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=11, day='last', hour=23, minute=59, second=59, round_year=True)]),

        # this autumn; ex: bu sonbahar
        ("THIS_FALL_REGEX", TYPE_DATESPAN,
         re.compile(r"^(?:(?:bu )?son ?bahar(?:{})?)$".format(CASE_SUFFIXES), re.UNICODE),
         [date_creator(month=9, day=1, hour=0, minute=0, second=0, round_year=True),
          date_creator(month=11, day='last', hour=23, minute=59, second=59, round_year=True)]),

        # ########### Date Period ##########

        ("EVERY_DAY_OF_WEEK_REGEX", TYPE_PERIOD,
         re.compile(r"^her (?:{} )?({})$".format(WEEK_EXPRESSION, DAYS_EXPRESSION), re.UNICODE),
         "week{}1".format(SPAN_SEPARATOR)),

        ("EVERY_WEEK_REGEX", TYPE_PERIOD,
         re.compile(r"^her (?:{})$".format(WEEK_EXPRESSION), re.UNICODE),
         "week{}monday".format(SPAN_SEPARATOR)),

        ("EVERY_MONTH_REGEX", TYPE_PERIOD,
         re.compile(r"^(?:(?:her )(?:{})|(?:aylık))$".format(MONTH), re.UNICODE),
         "month{}monday".format(SPAN_SEPARATOR)),

        ("EVERY_DAY_OF_MONTH_REGEX", TYPE_PERIOD,
         re.compile(r"^her (?:{}) ([0-3]?[0-9]){}?$".format(MONTH, CASE_SUFFIXES), re.UNICODE),
         "month{}1".format(SPAN_SEPARATOR)),

        ("EVERY_MONTH_OF_YEAR_REGEX", TYPE_PERIOD,
         re.compile(r"^her {} ({}) {}{}?$".format(YEAR_EXPRESSION, MONTHS_EXPRESSION,
                                                  MONTH, CASE_SUFFIXES), re.UNICODE),
         "year{}1".format(SPAN_SEPARATOR))
    ]

    @staticmethod
    def map_month_expr(month_expr):
        month_expression_map = {
            "ocak": re.compile(r"^(?:(([Oo]ca(k|(ğın)))|([Oo]ca)))$", re.UNICODE),
            "şubat": re.compile(r"^(([Şş]ubat(ın)?)|([Şş]ub))$", re.UNICODE),
            "mart": re.compile(r"^(([Mm]art(ın)?)|([Mm]ar))$", re.UNICODE),
            "nisan": re.compile(r"^(([Nn]isan(ın)?)|([Nn]is))$", re.UNICODE),
            "mayıs": re.compile(r"^(([Mm]ayıs(ın)?)|([Mm]ay))$", re.UNICODE),
            "haziran": re.compile(r"^(([Hh]aziran(ın)?)|([Hh]az))$", re.UNICODE),
            "temmuz": re.compile(r"^(([Tt]emmuz(un)?)|([Tt]em))$", re.UNICODE),
            "ağustos": re.compile(r"^(([Aa]ğustos(un)?)|([Aa]ğu))$", re.UNICODE),
            "eylül": re.compile(r"^(([Ee]ylül(ün)?)|([Ee]yl))$", re.UNICODE),
            "ekim": re.compile(r"^(([Ee]kim(in)?)|([Ee]ki))$", re.UNICODE),
            "kasım": re.compile(r"^(([Kk]asım(ın)?)|([Kk]as))$", re.UNICODE),
            "aralık": re.compile(r"^(([Aa]ralı(k|ğın))|([Aa]ra))$", re.UNICODE)
        }

        for month in month_expression_map:
            month_expr = re.sub(month_expression_map[month], month, month_expr)
        return month_expr

    def parse_date(self, input_expr):
        """
        Takes an input and return the corresponding date expression.
        Expects the whole input to be a date expression.
        :param input_expr: (String)
        :return: (datetime)
        """
        # Convert literal numbers into numbers, ex: dört -> 4
        # Regexes above need numerical numbers in order to work
        found_numbers = self.number_detector.find_all(input_expr)
        for i in range(len(found_numbers) - 1, -1, -1):
            if not re.sub(r"(?:[_, \-.\\/+=])", '', found_numbers[i]["text"]).isdigit():
                num_back = input_expr[found_numbers[i]["end_index"]:]
                _num = str(int(found_numbers[i]["value"]))
                input_expr = input_expr[:found_numbers[i]["start_index"]] + _num + num_back

        # Further preprocessing
        input_expr = turkish_lower(input_expr)
        input_expr = self.map_month_expr(input_expr)

        # Regex matching
        for rule in self.regex_list:
            rule_name, rule_type, rule_regex, date_func = rule

            if re.search(rule_regex, input_expr) is not None:
                if rule_type == self.TYPE_DATETIME:
                    assert callable(date_func)
                    return date_func(rule_regex, input_expr)

                elif rule_type == self.TYPE_DATESPAN:
                    assert isinstance(date_func, list) and len(date_func) == 2
                    return list(map(lambda date_func_x: date_func_x(rule_regex, input_expr), date_func))

                elif rule_type == self.TYPE_PERIOD:
                    assert isinstance(date_func, str)
                    period_key, period_value = date_func.split(self.SPAN_SEPARATOR)
                    if period_value.isnumeric():
                        period_value = re.match(rule_regex, input_expr).group(int(period_value))
                    period_dict = {period_key: period_value}
                    return period_dict

        # Some expressions can confuse the parser
        if ((not re.search(self.YEAR_ONLY_REGEX, input_expr)) and input_expr.isdigit()) or \
                re.findall(r"(?:[+=$])", input_expr):
            return None
        # If none of the rules above match get help
        return dateparser.parse(input_expr, languages=[self.lan])

    # internal merge function
    @staticmethod
    def merge_tokens(tokens):
        return ' '.join(tokens)

    def date_tagger(self, input_sentence):
        """
        Tokenizes the given input and tags date expressions. This is done by sliding a lookup window.
        Windows have sizes 1 to number of tokens.
        :param input_sentence: (string) input sentence
        :return:  (List(datetime)) sentence tokens that is either a datetime, datespan or None
        """
        tokens = input_sentence.split(' ')
        tags = list(map(lambda token: self.parse_date(token), tokens))

        for window in range(2, len(tokens) + 1):
            for i in range(0, len(tokens) - window + 1):
                window_expr = self.merge_tokens(tokens[i:i + window])
                window_val = self.parse_date(window_expr)

                if window_val is not None:
                    tags[i:i + window] = [window_val] * window

        return tags

    def find_all(self, text):
        """
        Create tag construct from tagged tokes
        index_offset = previous_token_lengths + white_space(#tokens -1)
        :param text: (string) provided input sentence
        :return: (tag construct)
        """
        tokens = text.split(' ')
        text_len = sum(list(map(lambda x: len(x), tokens))) + len(tokens) - 1
        tags = self.date_tagger(text)

        # Assert possible problems that can arise from tokenization
        assert text_len == len(text), "Characters lost during tokenization"
        assert len(tokens) == len(tags), "Number of tags and tokens do not match"

        res = []
        for i in range(len(tags)):
            tag = tags[i]

            if tag is not None:
                if (i > 0) and (tags[i - 1] == tag):
                    res[-1]["end_index"] += len(tokens[i]) + 1
                    res[-1]["text"] = self.merge_tokens([res[-1]["text"], tokens[i]])
                else:
                    tag_offset = sum(list(map(lambda x: len(x), tokens[:i]))) + len(tokens[:i + 1]) - 1

                    values = {
                        'start_index': tag_offset,
                        'end_index': tag_offset + len(tokens[i]) - 1,
                        'text': tokens[i]
                    }

                    if isinstance(tag, list):
                        values['type'] = self.TYPE_DATESPAN
                        values['start_date'] = tag[0]
                        values['end_date'] = tag[1]
                    elif isinstance(tag, dict):
                        values['type'] = self.TYPE_PERIOD
                        values['start_date'] = tag
                        values['end_date'] = tag
                    else:
                        values['type'] = self.TYPE_DATETIME
                        values['start_date'] = tag
                        values['end_date'] = tag

                    res.append(values)
        return res
