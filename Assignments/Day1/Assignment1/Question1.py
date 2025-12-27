#Question 1
#length of string
str=input("Enter a string: ")
print("Length of Str :",len(str))

#print number of words
words=str.split()
print("Number of Words :",len(words))

#number of vowels
vowels='aeiouAEIOU'
count=0
for char in str:
    if char in vowels:
        count+=1
print("Number of vowels :",count)
