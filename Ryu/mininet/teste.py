print(f"*=*=" * 20 + "*\n"
            f"*    {1 + 1}    *                     Itération num : {1 + 1}                 *   {1 + 1}         *\n" +
            f"*=*=" * 20 +"*")

print(f"*=*=" * 20 + "*\n"
        f"*     /*\_/*\                 Génération du trafic...                           *\n" +
        f"*=*=" * 20 +"*\n")

print(f"*=*=" * 20 + "*")
attack = 'TCP-SYN'
print(f"*=*=" * 20 + "*\n"
                    f"                      Exécution d'une inondation {attack}               \n" +
                    f"*=*=" * 20 +"*")
'''hotes = []
switchs = []

for i in range(4):
        host_index = i
        if i < 2  :
                switch_index =  4

        else:
                switch_index =  5
        hotes.append(host_index)
        hotes.append(switch_index)
switchs.append(hotes)
hotes.clear
print(switchs)

hotes = []
switchs = []
for rack in range(1, 5):
        if rack == 1:
                for i in range(4):
                        host_index = i
                        switch_index = 5 if i < 2 else 6
                        hotes.append((host_index, switch_index))
        elif rack == 2 :
                for i in range(4):
                        host_index = i + 4
                        switch_index = 7 if i+4 < 6 else 8
                        hotes.append((host_index, switch_index))
        elif rack == 3 :
                for i in range(4):
                        host_index = i + 8
                        switch_index = 9 if i+8 < 10 else 10
                        hotes.append((host_index, switch_index))

print(hotes)

hotes = []

for rack in range(1, 6):
    for i in range(4):
        host_index = i + (rack - 1) * 4
        switch_index = (rack - 1) * 2 + (i // 2) + 4
        hotes.append((host_index, switch_index))
        #self.addLink(hotes[host_index], switchs[switch_index])

print(hotes)
'''
'''hotes = []

for rack in range(1, 6):
        for i in range(4):
                host_index = i + (rack - 1) * 4
                switch_index = (rack - 1) * 2 + (i // 2) + 6
                hotes.append((f"h{host_index}, s{switch_index}"))

print(hotes)
hotes = []

for rack in range(1, 6):
        for i in range(1, 5):
                host_index = i + (rack - 1) * 4
                switch_index = (rack - 1) * 2 + ((i - 1)// 2) + 6
                hotes.append((f"h{host_index}, s{switch_index}"))

print(hotes)
switchs = []
for i in range(5):
    switchs.append((0, i + 1))
print(switchs)

switchs = []
for i in range(3):
        switchs.append((1, i + 6))
        switchs.append((3, i + 9))
        switchs.append((2, i + 12))

print(switchs)
for i in range(4):
        print((i//2) + 6)
for i in range(1, 5):
        print(((i-1)//2) + 6)
hotes = []
for rack in range(1, 6):
        for i in range(1, 5):
                host_index = i + (rack - 1) * 4
                switch_index = (rack - 1) * 2 + ((i-1) // 2) + 6
                hotes.append((host_index, switch_index))
print(hotes)'''