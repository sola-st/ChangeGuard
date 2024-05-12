def find_missing_number(nums):
    low , high  = min(nums), max(nums)
    missing_number = high
    for i in range(low, high):
        missing_number ^= i ^ nums[i - low]
    return missing_number
