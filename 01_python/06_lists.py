list_nn = [123,44,55]

for i in list_nn:
    print(i)

if 44 in list_nn:
    print(True)

lst_copy = list_nn.copy()

list_nn.sort()

list_nn.extend(list_nn)

print(list_nn)