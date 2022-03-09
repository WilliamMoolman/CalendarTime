from calendar import c
import json
import datetime
import numpy as np

# def load_json():
#     with open("events.json") as f:
#         events = json.loads(f.read())
#     return events['value']

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

# def reformat_events(events):
#     reformatted_events = []
#     for event in events:
#         start_time = datetime.datetime.strptime(event['start']['dateTime'].split('.')[0],"%Y-%m-%dT%H:%M:%S")
#         end_time = datetime.datetime.strptime(event['end']['dateTime'].split('.')[0],"%Y-%m-%dT%H:%M:%S")
#         duration = end_time - start_time
#         category = event["categories"][0] if len(event["categories"]) else "Other"
#         if event["bodyPreview"] == "created by Garmin Connect":
#             category = "Sport"
        
#         reformatted_events.append({
#             "start": start_time,
#             "duration": duration.total_seconds(),
#             "valid": is_event_valid(event, start_time),
#             "category": category,
#             "subject": subject,
#             "week": start_time.date() - datetime.timedelta(days = start_time.date().weekday()),
#         })
    
#     return reformatted_events

# def json_to_events(json_file):
#     events = load_json(json_file)
#     events = reformat_events(events)
#     return events

# def time_to_str(td):
#         days, hours, minutes = td.days, td.seconds//3600, (td.seconds//60)%60
#         return f"{days: >2} days {hours: >2} hours {minutes: >2} minutes"

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
        with open("events.json") as f:
            events = json.loads(f.read())['value']
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
            processed_events.append([week, category, subject, duration])
        return np.array(processed_events)
    
    # def get_totals(self, stringify=False, start_date=datetime.datetime(2020,1,1)):
    #     weeks = {}
    #     for event in self.events:
    #         if not event["valid"]: continue
    #         if event["start"] < start_date: continue
    #         week = event["week"]
    #         if week not in weeks.keys():
    #             weeks[week] = {"Total": 0, "Categories": {category: 0 for category in self.categories}}
            
    #         weeks[week]["Categories"][event["category"]] += event["duration"]
    #         weeks[week]["Total"] += 1
    
    #     if stringify:
    #         for week_key in weeks.keys():
    #             week = weeks[week_key]
    #             for category in week["Categories"].keys():
    #                 week["Categories"][category] = time_to_str(week["Categories"][category])
    #     return weeks
