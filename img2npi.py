from sys import argv
from PIL import Image
from struct import pack
import os
import glob

max_run_count = 0xFF #Could probably be higher for better compression

def writeInt32(val):
    return pack('I', val)

def writeInt16(val):
    return pack('H', val)

def writeInt8(val):
    return pack('B', val)

def toNpi(path):
    input_img = Image.open(path).convert("RGBA")
    input_pixels = input_img.load() # Create the pixel map
    img_width = input_img.size[0]
    img_height = input_img.size[1]

    def processLine(y):
        rv = bytearray()

        duplicate_count = 0
        unique_count = 0
        buffer = bytearray()

        def pixelToBuffer(px):
            nonlocal buffer
            if len(px)==3:
                buffer += bytearray([px[2], px[1], px[0]], 0)
            elif len(px)==4:
                buffer += bytearray([px[2], px[1], px[0], px[3]])
            else:
                print('Unsupported pixel format')

        def bufferToOutput():
            nonlocal rv, buffer, duplicate_count, unique_count
            if duplicate_count > 0:
                rv += writeInt8(duplicate_count)
                rv.append(0x10)
            else:
                rv += writeInt8(unique_count)
                rv.append(0xF0)

            rv += buffer
            buffer = bytearray()
            duplicate_count = 0
            unique_count = 0

        for x in range(img_width):
            px = input_pixels[x, y]

            duplicate = False
            if x < img_width-1:
                if px == input_pixels[x+1, y]:
                    duplicate = True
            elif x > 0:
                if px == input_pixels[x-1, y]:
                    duplicate = True

            if duplicate:
                ## Duplicate pixel
                if unique_count > 0:
                    bufferToOutput()

                if duplicate_count == 0:
                    pixelToBuffer(px)

                duplicate_count += 1
                if duplicate_count >= max_run_count:
                    bufferToOutput()

            else:
                ## Unique pixel
                if duplicate_count > 0:
                    bufferToOutput()

                unique_count += 1
                pixelToBuffer(px)

                if unique_count >= max_run_count:
                    bufferToOutput()

            if x == img_width-1:
                bufferToOutput()

        return rv

    img_data = bytearray()
    for y in range(img_height):
        result = processLine(y)
        img_data += writeInt16(len(result))
        img_data += result

    with open(f'{os.path.splitext(path)[0]}.npi', 'wb') as f:
        f.write(bytearray([0]*0x20))
        f.write(writeInt32(1))
        f.write(writeInt32(4))
        f.write(writeInt32(img_height))
        f.write(writeInt32(img_width))
        f.write(writeInt32(len(img_data)))
        f.write(bytearray([0]*0x0C))
        f.write(img_data)


def main():
    try:
        for path in argv[1:]:
            if os.path.isfile(path):
                print(f'Converting {path}')
                toNpi(path)
            elif os.path.isdir(path):
                for fname in glob.glob(os.path.join(path, '*.png')):
                    try:
                        print(f'Converting {fname}')
                        toNpi(fname)
                    except ValueError as e:
                        print(e)
            else:
                print(f"{path} doesn't exist")
    except KeyboardInterrupt:
        print('Canceling conversion')
    #except Exception as e:
    #    print(e)
    finally:
        print('Done')
    
    input("Press Enter to continue...")

if __name__=="__main__":
    main()