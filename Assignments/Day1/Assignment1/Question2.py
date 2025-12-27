#Question 2
numbers=input("Enter numbers separated by commas: ")
num_list=numbers.split(',')
even_count=0
odd_count=0
for num in num_list:
    if int(num)%2==0:
        even_count+=1
    else:
        odd_count+=1
print("Even numbers count :",even_count)
print("Odd numbers count :",odd_count)

