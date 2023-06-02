from sys import argv

with open(argv[1], 'rb') as f:
    data = f.read()
    print(data)

out = bytearray()

if len(data) != 0:
    if data[0] == 2:
        local_18 = data[1]
        local_14 = 0
        data = data[2:]
        local_10 = 11
        iVar1 = len(data)
        if 0 < iVar1:
            local_c = 1
            while iVar1 != 0:
                uVar2 = data[local_c - 1]
                if uVar2 - 10 < 4:
                    out.append(13)
                    # print("out is cr")
                elif uVar2 - 32 < 224:
                    uVar2 ^= local_10
                    local_10 = local_10 + uVar2 & 0x8000001f
                    if local_10 < 0:
                        local_10 = (local_10 - 1 | 0xffffffe0) + 1
                    out.append(uVar2)
                    local_14 += uVar2
                else:
                    out.append(uVar2)
                local_c += 1
                iVar1 -= 1
        local_14 &= 0x800000ff
        if local_14 < 0:
            local_14 = (local_14 - 1 | 0xffffff00) + 1
        if local_18 != local_14:
            print('something went wrong')
else:
    print('data is empty')

# print(f'out is {out}')
# print(f"decoded is {out.decode(encoding='sjis')}")

with open(f'{argv[1].replace(".cde", "")}.nps', 'wb') as f:
    f.write(out)
