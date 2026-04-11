from datetime import datetime, timedelta

class CalendarManager:
    def __init__(self):
        self.events = []

    def add_event(self, title, date_time):
        event = {
            "title": title,
            "datetime": date_time
        }
        self.events.append(event)
        return f"Event '{title}' added for {date_time}"

    def get_upcoming_events(self):
        now = datetime.now()
        return [e for e in self.events if e["datetime"] > now]

    def get_today_events(self):
        today = datetime.now().date()
        return [
            e for e in self.events
            if e["datetime"].date() == today
        ]

    def remove_event(self, title):
        self.events = [e for e in self.events if e["title"] != title]
        return f"Event '{title}' removed"

    def time_until_event(self, title):
        now = datetime.now()
        for e in self.events:
            if e["title"] == title:
                return e["datetime"] - now
        return "Event not found"