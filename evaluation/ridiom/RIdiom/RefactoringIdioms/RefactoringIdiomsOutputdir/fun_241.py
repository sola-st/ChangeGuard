def longestSub(ARRAY): 			
    ARRAY_LENGTH = len(ARRAY)
    if(ARRAY_LENGTH <= 1):  	
        return ARRAY
    PIVOT , isFound , i , LONGEST_SUB  = ARRAY[0], False, 1, []
    while(not isFound and i<ARRAY_LENGTH):
        if (ARRAY[i] < PIVOT):
            isFound , TEMPORARY_ARRAY  = True, [element for element in ARRAY[i:] if element >= ARRAY[i]]
            TEMPORARY_ARRAY = longestSub(TEMPORARY_ARRAY)
            if ( len(TEMPORARY_ARRAY) > len(LONGEST_SUB) ):
                LONGEST_SUB = TEMPORARY_ARRAY
        else:
            i+=1
    TEMPORARY_ARRAY = [ element for element in ARRAY[1:] if element >= PIVOT ]
    TEMPORARY_ARRAY = [PIVOT] + longestSub(TEMPORARY_ARRAY)
    if ( len(TEMPORARY_ARRAY) > len(LONGEST_SUB) ):
        return TEMPORARY_ARRAY
    else:
        return LONGEST_SUB
