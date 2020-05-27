def create_periods_list(label, period, end):
    if label == 'Quarter':
        periods = [dt for dt in period.range('months', 3)]
        if periods[-1] < end:
            dt = periods[-1]
            dt = dt.add(months=3)
            periods.append(dt)
    elif label == 'Month':
        periods = [dt for dt in period.range('months', 1)]
        if periods[-1] < end:
            dt = periods[-1]
            dt = dt.add(months=1)
            periods.append(dt)
    elif label == 'Year':
        periods = [dt for dt in period.range('months', 12)]
        if periods[-1] < end:
            dt = periods[-1]
            dt = dt.add(months=12)
            periods.append(dt)

    return periods
