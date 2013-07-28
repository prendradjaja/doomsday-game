import calendar
import datetime
import random
import os
import sys
import argparse

def main():
    args = parse_args()
    start, end = set_difficulty(args)
    test = set_test(args)
    date_gen = set_date_gen(args, test)

    play(start, end, date_gen, test)

def play(start, end, date_gen, test):
    right, tries = 0, 0
    try:
        while True:
            clear()
            right += test(start, end, date_gen)
            tries += 1
            print_score(right, tries)
            print()
            pause()
    except PlayerExit:
        print_score(right, tries, final=True)
    except EOFError:
        print()
        print_score(right, tries, final=True)

def print_score(right, tries, final=False):
    if final:
        adj = 'Final'
    else:
        adj = 'Current'
    if tries > 0:
        percent = right/tries * 100
        print('{a} score: {r}/{t} ({p:.2f}%)'.format(a=adj, r=right, t=tries, p=percent))
    else:
        print("You didn't even try!")

def set_test(args):
    if args.give_year:
        return test_day_in_year
    elif args.give_century:
        return test_year_in_century
    elif args.anchor:
        return test_anchor
    elif args.offset == 'y':
        return test_year_offset
    elif args.offset == 'd':
        return test_day_offset
    else:
        return test_weekday

def set_date_gen(args, test):
    if test is test_year_in_century:
        return random_year
    elif test is test_anchor:
        return random_century
    elif args.more_leap_years:
        return random_date_leap_weighted
    else:
        return random_date

def set_difficulty(args):
    if args.difficulty:
        return DIFFICULTY[args.difficulty]
    elif args.give_century or args.anchor:
        return DIFFICULTY['h']
    else: # For give-year, or by default
        return DIFFICULTY['m']

# Difficulty settings
DIFFICULTY = {'e': (1900, 2100),
              'm': (1600, 2400),
              'h': (1200, 9999)}

def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-d', '--difficulty', help=DIFFICULTY_HELP, choices='emh')
    parser.add_argument('-l', '--more-leap-years', help=LEAP_HELP, action='store_true')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-y', '--give-year', help=YEAR_HELP, action='store_true')
    group.add_argument('-c', '--give-century', help=CENTURY_HELP, action='store_true')
    group.add_argument('-a', '--anchor', help=ANCHOR_HELP, action='store_true')
    group.add_argument('-o', '--offset', help=OFFSET_HELP, choices='yd')

    return parser.parse_args()

DESCRIPTION = 'Tests you on day-of-week calculations for learning the Doomsday Rule. Responses can be full day names ("Tuesday") or three-letter abbreviations. ("tue")'

DIFFICULTY_KEY = ', '.join('{0}: {1}-{2}'.format(d, *DIFFICULTY[d]) for d in 'emh')

DIFFICULTY_HELP = 'Force a particular difficulty level, which can be e, m, or h. (for easy, medium, and hard) ' + DIFFICULTY_KEY
LEAP_HELP = 'Focuses testing on leap years by only using days in the beginning of the year, and increases the chance of the being a leap year.'
YEAR_HELP = "Ask for the weekday of a day in some year given that year's doomsday."
CENTURY_HELP = "Ask for the doomsday of a year in some century given that century's anchor."
ANCHOR_HELP = 'Ask for the anchor of a century.'
OFFSET_HELP = "Ask for the offset of a year (y) from its century's anchor or day (d) from its year's doomsday."

# Testing functions
def test_weekday(start, end, date_gen, give_year=False):
    year, month, day = date_gen(start, end)
    if give_year:
        print_doomsday(year)
    response = ask_weekday(year, month, day)
    correct_answer = get_weekday(year, month, day)
    return check_result(response, correct_answer)

def test_day_in_year(start, end, date_gen):
    return test_weekday(start, end, date_gen, True)

def test_year_in_century(start, end, date_gen, give_century=True):
    year = date_gen(start, end)
    if give_century:
        print_doomsday(year//100 * 100)
    response = ask_doomsday(year)
    return check_result(response, doomsday(year))

def test_anchor(start, end, date_gen):
    return test_year_in_century(start, end, date_gen, False)

# Needs to be fixed...
def test_random(tests):
    test = random.choice(tests)
    test()

# System functions
def system_cyg_compatible(cmd):
    if sys.platform == 'win32':
        os.system(cmd)
    elif sys.platform == 'cygwin':
        os.system('cmd /c ' + cmd)
    else:
        print('[some equivalent of Windows "{0}" command here]'.format(cmd))

def pause():
    system_cyg_compatible('pause')

def clear():
    system_cyg_compatible('cls')

# Random functions
def random_date(start, end):
    startdate = datetime.date(start, 1, 1)
    enddate = datetime.date(end, 1, 1)
    delta = enddate - startdate
    days = random.randrange(delta.days)
    date = datetime.date(start, 1, 1) + datetime.timedelta(days)
    return date.year, date.month, date.day

def random_date_leap_weighted(start, end):
    delta = datetime.timedelta(random.randrange(75))
    year = random.randint(start, end)
    leapyear = random.choice([True, False])
    if leapyear:
        oldyear = year
        year = year//4 * 4
    date = datetime.date(year, 1, 1) + delta
    return date.year, date.month, date.day

def random_year(start, end):
    return random.randint(start, end)

def random_century(start, end):
    return random.randint(start//100, end//100)*100


# Calendar calculations
def get_weekday(year, month, day):
    return calendar.day_name[calendar.weekday(year, month, day)]

def doomsday(year):
    return get_weekday(year, 12, 12)

# Output functions
def print_doomsday(year):
    print('Doomsday in {y} is {d}.'.format(y=year, d=doomsday(year)))

def check_result(response, correct_answer, gametracker=None, questioninfo=None):
    if response == correct_answer:
        print('Correct!'.format(response))
        return True
    else:
        print('Incorrect. The correct answer is {0}.'.format(correct_answer))
        if gametracker:
            gametracker.wrong_answer(questioninfo)
        return False

def date_string(year, month, day):
    date = datetime.date(year, month, day)
    month, day, year = [date.strftime('%' + s) for s in 'BdY']
    if int(day) < 10:
        day = day[1]
    return '{m} {d}, {y}'.format(m=month, d=day, y=year)

QUIT_HELP_STR = '(type "exit" to quit)'

# Input functions
def ask_weekday(year, month, day):
    print('What weekday is {d}? {q}'.format(d=date_string(year, month, day), q=QUIT_HELP_STR))
    return sanitized_weekday_input()

def ask_doomsday(year):
    print('What is doomsday in {y}? {q}'.format(y=year, q=QUIT_HELP_STR))
    return sanitized_weekday_input()

abbreviations = {
    'sun': 'Sunday',
    'mon': 'Monday',
    'tue': 'Tuesday',
    'wed': 'Wednesday',
    'thu': 'Thursday',
    'fri': 'Friday',
    'sat': 'Saturday',
    'tues': 'Tuesday',
    'thur': 'Thursday',
    'thurs': 'Thursday'}

def get_input():
    return input('>>> ').strip()

def sanitized_weekday_input():
    response = get_input()
    if response == 'exit':
        raise PlayerExit()
    if response in abbreviations:
        return abbreviations[response]
    if response not in calendar.day_name:
        invalid_input(response)
    return response

class PlayerExit(Exception):
    pass

# New feature! To sort...
def test_day_offset(ignore1, ignore2, ignore3):
    leap = random.choice([True, False])
    delta = datetime.timedelta(random.randrange(365 + leap))
    date = datetime.date(1999 + leap, 1, 1) + delta
    response = ask_day_offset(date, leap)
    return check_result(response, get_day_offset(date))

def date_string_short(month, day):
    date = datetime.date(2000, month, day)
    month, day = [date.strftime('%' + s) for s in 'Bd']
    if int(day) < 10:
        day = day[1]
    return '{m} {d}'.format(m=month, d=day)

def ask_day_offset(date, leap):
    adj = 'leap' if leap else 'non-leap'
    date_str = date_string_short(date.month, date.day)
    print('What is the offset (0 to 6) for {d} in a {a} year?'.format(d=date_str, a=adj))
    return sanitized_offset_input()

def get_day_offset(date):
    doomsday = datetime.date(date.year, 12, 12)
    delta = date - doomsday
    return delta.days % 7

def test_year_offset(ignore1, ignore2, ignore3):
    year = gametracker.pick_offset_year()
    response = ask_year_offset(year)
    questioninfo = ('year_offset', year)
    return check_result(response, get_year_offset(year), gametracker, questioninfo)

def ask_year_offset(year):
    print('What is the offset (0 to 6) for a year ending in {y}?'.format(y=year))
    return sanitized_offset_input()

def sanitized_offset_input():
    response = get_input()
    try:
        i = int(response)
    except ValueError:
        invalid_input(response)
        i = -1
    return i

def invalid_input(response):
    print('-- INVALID INPUT: {0} --'.format(response))

def get_year_offset(year):
    a = year // 12
    b = year % 12
    c = b // 4
    return (a + b + c) % 7

def rand_prob(p):
    """Return true with P probability."""
    return random.random() < p

class gametracker:
    def __init__(self):
        self.offset_years = []
    def pick_offset_year(self):
        if self.offset_years and rand_prob(0.25):
            year = random.choice(self.offset_years)
            self.offset_years.remove(year)
            return year
        else:
            return random.randrange(100)
    def wrong_answer(self, questioninfo):
        question, *info = questioninfo
        if question == 'year_offset':
            year = info[0]
            self.offset_years.extend([year]*2)

gametracker = gametracker()

main()
