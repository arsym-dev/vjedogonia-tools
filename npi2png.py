from sys import argv
from PIL import Image
from struct import unpack
import os
import glob

def readInt32(data, offset):
    return unpack('I', data[offset:offset+4])[0]

def readInt16(data, offset):
    return unpack('H', data[offset:offset+2])[0]

def readInt8(data, offset):
    return unpack('B', data[offset:offset+1])[0]


def toPng(path):
    with open(path, 'rb') as f:
        data = f.read()

    header_size = 0x40

    npi_type = readInt32(data, 0x24)
    img_height = readInt32(data, 0x28)
    img_width = readInt32(data, 0x2C)
    img_data_size = readInt32(data, 0x30)
    img_data = data[header_size:]

    if (img_width == 0 or img_height == 0):
        raise ValueError('Image width or height is zero')

    if npi_type == 0x03:
        ## 24 bit
        output_img = Image.new('RGB', (img_width, img_height))
        output_pixels = output_img.load()

        data_ptr = 0
        for y in range(img_height):
            x = 0
            buffer_size = readInt16(img_data, data_ptr)
            data_ptr += 2
            # if instr_len == 5:
            #     px_data = unpack('BBB', data[data_ptr+2:data_ptr+5])
            # else:
            #     raise ValueError(f"Unsupported read size: {uStack5596}, expected 5")

            iVar4 = 0
            while iVar4 < img_width:
                instr = readInt16(img_data, data_ptr)
                data_ptr += 2

                px_count = instr & 0xfff
                if (instr & 0xf000) == 0:
                    px_data = (img_data[data_ptr+2], img_data[data_ptr+1], img_data[data_ptr])
                    data_ptr += 3
                    for _ in range(px_count):
                        output_pixels[x, y] = px_data
                        x += 1

                elif (instr & 0xf000) == 0xf000:
                    for _ in range(px_count):
                        output_pixels[x, y] = (img_data[data_ptr+2], img_data[data_ptr+1], img_data[data_ptr])
                        x += 1
                        data_ptr += 3
                iVar4 += px_count

    elif npi_type == 0x04:
        ## 32 bit
        output_img = Image.new('RGBA', (img_width, img_height))
        output_pixels = output_img.load() # Create the pixel map
        img_ptr = 0

        for y in range(img_height):
            x = 0

            line_length = readInt16(img_data, img_ptr)
            img_ptr += 2

            line_start = img_ptr
            line_end = img_ptr + line_length
            while img_ptr < line_end:
                px_param = img_data[img_ptr]
                px_opcode = img_data[img_ptr+1]
                img_ptr += 2

                if px_opcode == 0x10:
                    ## Copy the next pixel #px_param times
                    px = (img_data[img_ptr+2], img_data[img_ptr+1], img_data[img_ptr], img_data[img_ptr+3])
                    img_ptr += 4
                    for _ in range(px_param):
                        output_pixels[x, y] = px
                        x += 1

                elif px_opcode == 0xF0:
                    ## Copy the next #px_param pixels directly
                    for _ in range(px_param):
                        output_pixels[x, y] = (img_data[img_ptr+2], img_data[img_ptr+1], img_data[img_ptr], img_data[img_ptr+3])
                        img_ptr += 4
                        x += 1

    if npi_type == 0x23:
        ## 24 bit
        output_img = Image.new('RGB', (img_width, img_height))
        output_pixels = output_img.load()

        data_ptr = 0x180
        ## I have no idea what's in these first 0x180 bytes, but the game completely skips them
        px_ptr = data_ptr

        for y in range(img_height):
            # buffer_size = readInt16(img_data, data_ptr)
            # data_ptr += 2
            # px_ptr = data_ptr
            # data_ptr += buffer_size

            px_ptr += 2

            b = 0
            r = 0
            g = 0

            """
            if ((val < 0x3e) || ((byte)(val - 0x3f) < 0x40)) {
              uStack5600 = ((uint)*(byte *)px_data_ptr % 5 + uStack5600) - 2
              uStack5604 = ((int)(((ulonglong)*(byte *)px_data_ptr / 5) % 5) + uStack5604) - 2
              uVar6 = (uVar6 + *(byte *)px_data_ptr / 0x19) - 2
            }
            else if (val == 0x7f) {
              uVar6 = (uint)*(byte *)((int)px_data_ptr + 1)
              uStack5604 = (uint)*(byte *)(px_data_ptr + 1)
              px_data_ptr = (ushort *)((int)px_data_ptr + 3)
              uStack5600 = (uint)*(byte *)px_data_ptr
            }
            else if ((byte)(val + 0x80) < 0x80) {
              val = *(byte *)px_data_ptr
              px_data_ptr = (ushort *)((int)px_data_ptr + 1)
              uVar4 = (uint)(CONCAT11(val,*(byte *)px_data_ptr) & 0x7fff)
              uStack5600 = (((int)uVar4 >> 10) + uStack5600) - 0xf
              uStack5604 = (((int)uVar4 >> 5 & 0x8000001fU) + uStack5604) - 0xf
              uVar6 = (uVar6 + (uVar4 & 0x8000001f)) - 0xf
            }
            *(undefined *)(iVar3 + iVar7 * 3) = (undefined)uStack5600
            *(undefined *)(iVar3 + 1 + iVar7 * 3) = (undefined)uStack5604
            *(char *)(iVar3 + 2 + iVar7 * 3) = (char)uVar6
            px_data_ptr = (ushort *)((int)px_data_ptr + 1)
            iVar7 = iVar7 + 1
            x = x + -1
            """

            for x in range(img_width):
                val = readInt8(img_data, px_ptr)

                if val < 0x7f:
                    r = (r + val % 5) - 2
                    g = (g + (val // 5) % 5) - 2
                    b = (b + val // 0x19) - 2

                elif val == 0x7f:
                    b = readInt8(img_data, px_ptr+1)
                    g = readInt8(img_data, px_ptr+2)
                    r = readInt8(img_data, px_ptr+3)
                    px_ptr += 3

                else:
                    uVar4 = ((val << 8) + readInt8(img_data, px_ptr+1)) & 0x7FFF
                    px_ptr += 1
                    r = ((uVar4 >> 10) + r) - 0xf
                    g = ((uVar4 >> 5 & 0x1f) + g) - 0xf
                    b = (b + (uVar4 & 0x1f)) - 0xf

                b %= 256
                g %= 256
                r %= 256

                output_pixels[x, y] = (b, g, r)
                px_ptr += 1

        # px = output_pixels[8, 1]
        # print(f'{px[0]:02X}{px[1]:02X}{px[2]:02X}')
        # print(f'Dim: ({img_width}, {img_height}), Pos: ({x}, {y})')
        # print(f'Size: 0x{len(data):02X}, Ptr: 0x{px_ptr:02X}')


    else:
        raise ValueError(f'Error: Unsupported NPI type: 0x{npi_type:02X}')

    # output_img.show()
    output_img.save(f'{os.path.splitext(path)[0]}.png')

def main():
    try:
        for path in argv[1:]:
            if os.path.isfile(path):
                print(f'Converting {path}')
                toPng(path)
            elif os.path.isdir(path):
                for fname in glob.glob(os.path.join(path, '*.npi')):
                    try:
                        print(f'Converting {fname}')
                        toPng(fname)
                    except ValueError as e:
                        print(e)
            else:
                print(f"{path} doesn't exist")
    except KeyboardInterrupt:
        print('Canceling conversion')
    # except Exception as e:
    #     print(e)
    finally:
        print('Done')
    
    input("Press Enter to continue...")
    

if __name__=="__main__":
    main()