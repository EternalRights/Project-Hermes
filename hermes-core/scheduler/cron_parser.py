from datetime import datetime, timedelta, timezone


class CronParser:
    FIELD_NAMES = ['minute', 'hour', 'day', 'month', 'weekday']
    FIELD_RANGES = {
        'minute': (0, 59),
        'hour': (0, 23),
        'day': (1, 31),
        'month': (1, 12),
        'weekday': (0, 6),
    }

    @classmethod
    def parse(cls, expression):
        fields = expression.strip().split()
        if len(fields) != 5:
            raise ValueError(f"Cron expression must have 5 fields, got {len(fields)}")
        parsed = {}
        for i, name in enumerate(cls.FIELD_NAMES):
            parsed[name] = cls._parse_field(fields[i], *cls.FIELD_RANGES[name])
        return parsed

    @classmethod
    def _parse_field(cls, field, min_val, max_val):
        values = set()
        for part in field.split(','):
            if '/' in part:
                base, step = part.split('/', 1)
                step = int(step)
                if base == '*':
                    start = min_val
                else:
                    start = int(base)
                for v in range(start, max_val + 1, step):
                    values.add(v)
            elif '-' in part:
                start, end = part.split('-', 1)
                for v in range(int(start), int(end) + 1):
                    values.add(v)
            elif part == '*':
                values = set(range(min_val, max_val + 1))
                return values
            else:
                val = int(part)
                if val < min_val or val > max_val:
                    raise ValueError(f"Value {val} out of range [{min_val}, {max_val}]")
                values.add(val)
        return values

    @classmethod
    def next_run_time(cls, expression, after=None):
        if after is None:
            after = datetime.now(timezone.utc)
        parsed = cls.parse(expression)
        dt = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
        for _ in range(366 * 24 * 60):
            if (dt.minute in parsed['minute'] and
                dt.hour in parsed['hour'] and
                dt.day in parsed['day'] and
                dt.month in parsed['month'] and
                dt.weekday() in parsed['weekday']):
                return dt
            dt += timedelta(minutes=1)
        raise ValueError("No valid next run time found within reasonable range")
