
import datetime
from calendar_providers.base_provider import BaseCalendarProvider, CalendarEvent
from utility import is_stale
import os
import logging
import pickle
import icalevents.icalevents
from dateutil import tz
from utility import get_formatted_time, update_svg, configure_logging, get_formatted_date, configure_locale

ttl = float(os.getenv("CALENDAR_TTL", 1 * 60 * 60))

class ICSCalendar(BaseCalendarProvider):

    def __init__(self, ics_calendar_url, max_event_results, from_date, to_date):
        self.ics_calendar_url = ics_calendar_url
        self.max_event_results = max_event_results
        self.from_date = from_date
        self.to_date = to_date

    def get_calendar_events(self, overrideTtl=None) -> list[CalendarEvent]:

        if overrideTtl:
            setTtl = overrideTtl
        else:
            setTtl = ttl

        calendar_events = []
        ics_calendar_pickle = 'cache_ics.pickle'
        if is_stale(os.getcwd() + "/" + ics_calendar_pickle, setTtl):
            logging.debug("Pickle is stale, fetching ICS Calendar")

            # ICS_PERSONAL
            personal_url = os.getenv("ICS_PERSONAL")
            logging.debug("Getting personal events")
            ics_events1 = icalevents.icalevents.events(personal_url, start=self.from_date, end=self.to_date)
            logging.debug("Getting work events")
            ics_events2 = icalevents.icalevents.events(self.ics_calendar_url, start=self.from_date, end=self.to_date)
            logging.debug("Done getting events")
            ics_events = ics_events1 + ics_events2

            ics_events.sort(key=lambda x: x.start.replace(tzinfo=None))

            # logging.debug(ics_events)

            for ics_event in ics_events[0:self.max_event_results]:
                event_end = ics_event.end

                # CalDav Calendar marks the 'end' of all-day-events as
                # the day _after_ the last day. eg, Today's all day event ends tomorrow!
                # So subtract a day, if the event is an all day event
                if ics_event.all_day:
                    event_end = event_end - datetime.timedelta(days=1)

                # convert to local timezone
                event_end = ics_event.end.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
                event_start = ics_event.start.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())

                logging.debug(ics_event.summary, get_formatted_date(event_end), get_formatted_date(event_start))

                if event_end > datetime.datetime.now().astimezone(tz.tzlocal()) and ics_event.summary != 'Lunch':
                    calendar_events.append(CalendarEvent(ics_event.summary, event_start, event_end, ics_event.all_day))

            with open(ics_calendar_pickle, 'wb') as cal:
                pickle.dump(calendar_events, cal)
        else:
            logging.info("Found in cache")
            with open(ics_calendar_pickle, 'rb') as cal:
                calendar_events = pickle.load(cal)

        return calendar_events
