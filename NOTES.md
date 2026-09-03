# What I checked, and what the agent got wrong
first i asked Bob to find all problems it finds the files. it found 10.
i checked all 10 bugs that needed to be fixed and the solutions suggested by Bob. almost all of them were true, except these:

1. it found a bug in 'last = car.get("last_service_km", 0)' which wrongly flags car. the diagnosis was true, but the soltion was a little dirty code. it wanted to replace it by
    
    last = car.get("last_service_km")
    if last is None:
        return False

but i told it to do this:

    if "last_service_km" not in car:
        return False
    last = car["last_service_km"]

if a car record somehow has "last_service_km": None explicitly set (a data entry error), fist one returns False silently while second one would still crash on the subtraction.
in practice that distinction is unlikely to matter, but the "last_service_km" not in car check is strictly more precise about why we're bailing out — it only fires on a genuinely absent key, not on a null value.

2. it made this in 'fleet_report.py':

    def car_wear(car):
        last = car.get("last_service_km")
        if last is None:
            return 0.0          # ← treated as 0% worn in the average
        ...

    def fleet_summary(fleet):
        total = 0.0
        for car in fleet:
            total += car_wear(car)   # ← 0.0 added to the total
        average = total / len(fleet) # ← len(fleet) includes the car with no reading

The car's wear is genuinely unknown — not zero. Pulling it into the average as 0 % pulls the fleet average down, silently, every time a car with no reading is in the fleet. The report prints a lower average wear than the fleet actually has.

then it changed to this:
    
    def fleet_summary(fleet: list) -> dict:
        total = 0.0
        wear_count = 0          # only cars with a known reading
        due = 0
        for car in fleet:
            if "last_service_km" in car:
                total += car_wear(car)
                wear_count += 1
            if needs_service(car):
                due += 1
        average = total / wear_count if wear_count > 0 else 0.0
        return {"count": len(fleet), "due": due, "average_wear": average}

The count key still reflects the full fleet size (correct — the report should say how many cars it covers). The average_wear is now the average over only the cars we actually have data for.

## What the agent got wrong
it didnt get any prompt wrong, except the fist time i told it to read files and it made a bad report that i didnt like it because it was complicated, then i asked it to do it more neet and with a schematic of how files work.

## What I checked before I accepted its work
i ran these 3 things:
1. 'test_km_wachter.py':  
test_almost_due_car_is_flagged -- It passing proves the bug is gone.
test_missing_reading_is_not_treated_as_zero : proves the other half of the fix didn't break the missing-reading case.

2. this code:
from km_wachter import wear_percent, WARN_AT_PERCENT
print(wear_percent(14900, 15000))
print(wear_percent(12000, 15000) >= WARN_AT_PERCENT)

the output was: 
99.33333333333333
True


## What the data actually said
What predicts breakdown: km since last service , daily km driven, and load factor.

What doesn't: total odometer mileage and age — near-zero separation in both cases. A high-mileage old car that's well-serviced and lightly used is safer than a new car driven hard and overdue for service.