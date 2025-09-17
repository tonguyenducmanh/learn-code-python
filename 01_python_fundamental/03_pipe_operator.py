# without pipe operator
# result = summarize(filter_data(load_csv("data.csv")))

class Pipe:
    def __init__(self, value):
        self.value = value

    def __or__(self, func):
        self.value = func(self.value)
        return self

    def result(self):
        return self.value

# Instead of reading a file, just return sample data
def load_csv(path):
    # Simulate CSV data as list of lists
    return [
        ["name", "city", "score"],
        ["Alice", "Seattle", "60"],
        ["Bob", "Portland", "40"],
        ["Charlie", "San Francisco", "80"],
    ]

def filter_data(rows):
    # skip header row
    return [r for r in rows[1:] if int(r[2]) > 50]

def summarize(rows):
    return {"count": len(rows), "first_row": rows[0]}

# Using the pipe with no actual file reading
report = (
    Pipe("data.csv")
    | load_csv
    | filter_data
    | summarize
).result()

print(report)
