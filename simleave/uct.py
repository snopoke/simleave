from datetime import date
from dateutil.relativedelta import relativedelta
from workalendar.africa import SouthAfrica

cal = SouthAfrica()


class LeaveTaken(object):
    def __init__(self, startdate, enddate):
        assert startdate <= enddate
        self.startdate = startdate
        self.enddate = enddate

        self.duration_cal = (self.enddate - self.startdate).days
        self.duration = 0
        for i in range(self.duration_cal + 1):
            cur = self.startdate + relativedelta(days=i)
            if cal.is_working_day(cur):
                self.duration += 1

    def in_date(self, cur_date):
        return cur_date <= self.startdate <= (cur_date + relativedelta(months=1))

    def __lt__(self, other):
        return self.startdate < other.startdate

    def __eq__(self, other):
        return self.startdate == other.startdate and self.enddate == other.enddate

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "{l.duration} ({l.startdate} - {l.enddate})".format(l=self)


leave_schedule = sorted([
    LeaveTaken(date(2014, 5, 2), date(2014, 5, 2)),
    LeaveTaken(date(2014, 4, 29), date(2014, 4, 30)),
    LeaveTaken(date(2014, 2, 6), date(2014, 2, 10)),
    LeaveTaken(date(2014, 1, 17), date(2014, 1, 17)),
    LeaveTaken(date(2014, 1, 2), date(2014, 1, 10)),
    LeaveTaken(date(2013, 12, 23), date(2013, 12, 31)),
    LeaveTaken(date(2013, 9, 23), date(2013, 9, 27)),
    LeaveTaken(date(2013, 8, 8), date(2013, 8, 8)),
    LeaveTaken(date(2013, 1, 2), date(2013, 1, 11)),
    LeaveTaken(date(2012, 12, 21), date(2012, 12, 31)),
    LeaveTaken(date(2012, 11, 5), date(2012, 11, 13)),
    LeaveTaken(date(2012, 4, 30), date(2012, 4, 30)),
    LeaveTaken(date(2012, 4, 23), date(2012, 4, 26)),
    LeaveTaken(date(2012, 4, 19), date(2012, 4, 20)),
    LeaveTaken(date(2012, 2, 17), date(2012, 2, 17)),
    LeaveTaken(date(2012, 1, 3), date(2012, 1, 6)),
    LeaveTaken(date(2011, 12, 28), date(2011, 12, 30)),
    LeaveTaken(date(2011, 7, 15), date(2011, 7, 22)),
    LeaveTaken(date(2011, 6, 17), date(2011, 6, 17)),
    LeaveTaken(date(2011, 5, 20), date(2011, 5, 20)),
])


def check_overlap(leave):
    prev = None
    for l in leave:
        if prev:
            assert prev.enddate < l.startdate, "Leave overlapping: {}, {}".format(prev, l)
        prev = l


check_overlap(leave_schedule)


class LeaveBuckets(object):
    def __init__(self):
        self.comp_1 = 0
        self.comp_2 = 0
        self.accum = 0

    @property
    def total(self):
        return self.comp_1 + self.comp_2 + self.accum

    def can_take_leave(self, duration):
        return duration <= self.total

    def consume_leave(self, current_date, schedule):
        leave_taken = 0
        while schedule:
            current = schedule[0]
            if current.in_date(current_date):
                duration = current.duration
                if not self.can_take_leave(duration):
                    print "Not enough leave: {}".format(current)

                leave_taken += duration
                self.take_leave(duration)
                schedule.remove(current)
            else:
                break

        return schedule, leave_taken


    def take_leave(self, duration):
        rem = self.comp_1 - duration
        if rem < 0:
            self.comp_1 = 0
            rem = self.comp_2 - abs(rem)
            if rem < 0:
                self.comp_2 = 0
                rem = self.accum - abs(rem)
                if rem < 0:
                    self.comp_1 = rem
                    self.accum = 0
                else:
                    self.accum = rem
            else:
                self.comp_2 = rem
        else:
            self.comp_1 = rem

    def accumulate(self, amount):
        self.comp_1 += amount

    def rollover(self):
        self.accum += min(self.comp_2, 7)
        self.accum = min(self.accum, 42)
        self.comp_2 = self.comp_1
        self.comp_1 = 0

    def __repr__(self):
        return "{}, {}, {}".format(self.comp_1, self.comp_2, self.accum)


leave_buckets = LeaveBuckets()

start_date = date(year=2011, month=1, day=1)
end_date = date(year=date.today().year + 1, month=1, day=1)

leave_per_annum = 26
leave_per_month = round(float(leave_per_annum) / 12, 2)

current_date = start_date

print 'Date, Compulsory 1, Compulsory 2, Accumulated, Leave taken'
leave_taken = None
while current_date <= end_date:

    leave_schedule, leave_taken = leave_buckets.consume_leave(current_date, leave_schedule)

    print "{}, {}, {}".format(current_date, leave_buckets,
                              "Leave taken: {} days".format(leave_taken) if leave_taken else '')

    current_date = current_date + relativedelta(months=1)
    leave_buckets.accumulate(leave_per_month)
    if current_date.month == 1:
        leave_buckets.rollover()
        print