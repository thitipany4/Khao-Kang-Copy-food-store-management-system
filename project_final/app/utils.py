from calendar import HTMLCalendar
from datetime import datetime as dtime, date, time
import datetime

from .calculator import calculator
from .models import *
from django.urls import reverse



class EventCalendar(HTMLCalendar):
    def __init__(self, events=None):
        super(EventCalendar, self).__init__()
        self.events = events

    def formatday(self, day, weekday,month):
        """
        Return a day as a table cell.
        """
        show_text = ""
        date = f'{month}-{day}'
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            events_for_day = Transaction.objects.filter(date=date)  # Assuming Event is your model and 'date' is the field storing the event date
            sum_expenses,sum_income = calculator(events_for_day)
            sum = sum_income - sum_expenses
            if sum>0:
                total = f'<div class="num-total-plus">+{sum}</div>'
            else:
                total = f'<div class="num-total-negative">{sum}</div>'
            show_text = ""
            if events_for_day.exists():
                show_text += f'''<div class="text-event">
                    <div class="text-day">
                        {day}
                    </div>
                    <div class="text-expenses"> 
                        <div class="str-expenses">รายจ่าย</div>
                        <div class="num-expenses">{sum_expenses}</div>
                    </div>
                    <div class="text-income"> 
                        <div class="str-income">รายรับ</div>
                        <div class="num-income">{sum_income}</div>
                    </div>
                    <div class="text-total"> 
                        {total}
                    </div>'''
            else:   
                 show_text += f'''<div class="text-event">
                    <div class="text-day">
                        {day}
                    </div>
                    <div class="text-expenses"> 
                        <div class="str-expenses"></div>
                        <div class="num-expenses"></div>
                    </div>
                    <div class="text-income"> 
                        <div class="str-income"></div>
                        <div class="num-income"></div>
                    </div>
                    <div class="text-total"> 
                        <div class="num-total"></div>
                    </div>'''
    
            
            link = reverse("show-note", args=[date])  # Change "apply" to your desired URL name
            # Customize the HTML markup for each day cell here
            day_cell = f'<td class="calendar-day">'
            day_cell += f'<a href="{link}" class="day-link"><span class="day-number">{show_text}</span></a>'  # Link for the day
            day_cell += f'<div class="day-content"></div>'  # Content for the day
            day_cell += '</td>'
            return day_cell

    def formatweek(self, theweek,month):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd,month) for (d, wd) in theweek)
        return '<tr class=box-each-day>%s</tr>' % s



    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        print('....................')
        month = f'{theyear}-{themonth}'
        # print(month)

        v = []
        a = v.append
        a('<table class="body-calendar">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week,month))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)