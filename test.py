from datetime import datetime


now = datetime.now()

print(f"{now.date()}")
str = '2020-12-1'
str = str.split('-')
print(len(str))
type(now)
print(type(now.year))