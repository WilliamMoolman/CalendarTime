import datetime

def print_from_date(start_date, weeks):
    for week_key in sorted(weeks.keys()):
        week_start = datetime.datetime.strptime(week_key+"-1", "%G-%V-%w")
        if week_start < start_date: continue
        print(f"{week_key}\tTotal: {weeks[week_key]['Total']}")
        for category in weeks[week_key]["Categories"].keys():
            print(f"{category: <10}\t{weeks[week_key]['Categories'][category]}")
