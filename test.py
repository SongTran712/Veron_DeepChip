import re

def starts_with_number_dot(s):
    pattern = r"^\d+(?:\.\d+)*\.?\s+\S.*"  
    print(bool(re.match(pattern, s)))
    return bool(re.match(pattern, s))

print(starts_with_number_dot("1.2. dasd"))  # Should return True
print(starts_with_number_dot("1.2 dasd"))   # Should return True
print(starts_with_number_dot("1 dasd"))     # Should return True
print(starts_with_number_dot("1.2.3.4. dasd")) # Should return True
print(starts_with_number_dot("1.2."))       # Should return False (no word after space)
