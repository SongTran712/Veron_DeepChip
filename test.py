import re

def starts_with_number_dot(s):
    return bool(re.match(r'^\d+\.', s))


pattern = r"^\d"

text1 = "123. Hello"   # Matches (starts with a number)
# text2 = "Hello 123"   # Does not match (starts with a letter)

# Check if text starts with a number
print(starts_with_number_dot(text1)) 
print(text1) 