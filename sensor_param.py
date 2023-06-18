num = 400
k = (num-1)/2
sum = 0
for i in range(num):
    sum += pow(k, 2)
    k = k-1

print(sum)

