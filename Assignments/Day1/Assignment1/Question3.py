#Question 3
import pandas as pd
#a
df=pd.read_csv('D:\IIT-GENAI-94391\Assignments\product.csv')
#b
print(df)
#c
row_count=len(df)
print("Number of rows:",row_count)
#d 
count_above_500=len(df[df['price']>500])
print("Number of products priced above 500:",count_above_500)
#e 
avg=df['price'].mean()
print("Average price :",avg)
#f 
category=input("Enter category : ")
products=df[df['category']==category]
print("Products in category",category,":",products)
#g
quantity=df['quantity'].sum()
print("Total quantity :",quantity)

