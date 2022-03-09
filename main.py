from datetime import datetime
from events import Events
from visualise import print_from_date

def main():
    events = Events("combined.json")
    totals = events.get_totals(stringify=True)
    print_from_date(datetime(2022,1,1), totals)

if __name__ == "__main__":
    main()