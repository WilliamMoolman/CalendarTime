from calendar import c
import json
import datetime
import numpy as np


def is_event_valid(event, start_time):
    if event['isAllDay']:         return False
    if event['showAs'] == "free": return False
    if start_time > datetime.datetime.now(): return False
    return True

def determine_subject(event):
    with open("aliases.json") as f:
        aliases = json.loads(f.read())
    for k in aliases.keys():
        for a in aliases[k]:
            if a in event['subject']: return k 

class Events():
    def __init__(self) -> None:
        self.aliases = {}
        with open("aliases.json") as f:
            aliases = json.loads(f.read())
            for k in aliases.keys():
                for a in aliases[k]:
                    self.aliases[a] = k
        with open('schedule.json') as f:
            self.schedule = json.loads(f.read())
            for week in self.schedule.keys():
                self.schedule[week]['begin'] = datetime.datetime.strptime(self.schedule[week]['begin'],"%Y-%m-%d").date()
                self.schedule[week]['end'] = datetime.datetime.strptime(self.schedule[week]['end'],"%Y-%m-%d").date()

        self.events = self.get_events()

    def get_subject(self, event):
        for a in self.aliases.keys():
            if a in event['subject']:
                return self.aliases[a]

    def get_week(self, start_time):
        for week in self.schedule.keys():
            if start_time.date() >= self.schedule[week]['begin']:
                if start_time.date() <= self.schedule[week]['end']:
                    return week
            else:
                return "Before"
        return "After"

    def get_events(self):
        with open("data/events.json") as f:
            events = json.loads(f.read())
        processed_events = []
        for event in events:
            
            # Calculate duration (as timedelta)
            start_time = datetime.datetime.strptime(event['start']['dateTime'].split('.')[0],"%Y-%m-%dT%H:%M:%S")
            end_time = datetime.datetime.strptime(event['end']['dateTime'].split('.')[0],"%Y-%m-%dT%H:%M:%S")
            duration = end_time - start_time

            # Skip if invalid event
            if not is_event_valid(event,start_time): continue

            # Categories
            category = event["categories"][0] if len(event["categories"]) else "Other"
            if event["bodyPreview"] == "created by Garmin Connect":
                category = "Sport"
            
            subject = self.get_subject(event)
            week = self.get_week(start_time)
            processed_events.append([week, category, subject, start_time, end_time, duration])
        return np.array(processed_events)
