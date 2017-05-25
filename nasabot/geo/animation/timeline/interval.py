import datetime


class Interval:
    def __init__(self, from_date, to_date, step=datetime.timedelta(days=1)):
        self.from_date = from_date
        self.to_date = to_date
        self.step = step

    def __iter__(self):
        self.current_date = self.from_date
        return self

    def __next__(self):
        if self.current_date > self.to_date:
            raise StopIteration
        current_date = self.current_date.date()
        self.current_date += self.step
        return {
            'date': current_date.isoformat(),
        }
