from sys import argv
from PIL import Image
from struct import unpack, pack
import os

def readInt32(data, offset):
    return unpack('I', data[offset:offset+4])[0]

def readInt16(data, offset):
    return unpack('H', data[offset:offset+2])[0]

def writeInt32(val):
    return pack('I', val)

def writeInt16(val):
    return pack('H', val)

def writeInt8(val):
    return pack('B', val)

class FileEntry:
    offset = 0
    size = 0
    ukn5 = 0
    ukn6 = 0
    fname = ""
    data = None

    def __init__(self, data=None):
        if data:
            self.deserialize(data)

    def serialize(self):
        return writeInt32(self.offset) + writeInt32(self.size) + writeInt16(self.ukn5) + writeInt16(self.ukn6)

    def deserialize(self, data):
        self.offset = readInt32(data, 0x00)
        self.size = readInt32(data, 0x04)
        self.ukn5 = readInt16(data, 0x08)
        self.ukn6 = readInt16(data, 0x0A)


def extractPck(pck_path):
    output_dir = os.path.splitext(pck_path)[0]

    with open(pck_path, 'rb') as f:
        data = f.read()

    file_count = readInt32(data, 0x00)
    filename_table_length = readInt32(data, 0x04)
    unk1 = readInt16(data, 0x08)
    unk2 = readInt16(data, 0x0A)

    print(f"{file_count} files to unpack")

    ## Get file info
    data_ptr = 0x0C
    file_entries = []
    for _ in range(file_count-1):
        file_entries.append(FileEntry(data[data_ptr:data_ptr+0x0C]))
        data_ptr += 0x0C

    filename_table = data[data_ptr:data_ptr+filename_table_length].split(b'\r')[:-1]
    data_ptr += filename_table_length


    ## Get file names
    fnames = []
    for fname in filename_table:
        fnames.append(fname.decode('shift-jis'))


    pack_fname = ""
    for i, fname in enumerate(fnames):
        if i == 0:
            pack_fname = fname
        else:
            file_entries[i-1].fname = fname


    ## Save list file
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(os.path.join(output_dir, '_list.txt'), 'w', encoding='utf8') as f:
        for idx, fname in enumerate(fnames):
            if idx == 0:
                f.write(f'{fname},{unk1},{unk2}\n')
            else:
                fe = file_entries[idx-1]
                f.write(f'{fname},{fe.ukn5 & 0xffff},{fe.ukn6 & 0xffff}\n')


    ## Unpack files
    for file_info in file_entries:
        with open(os.path.join(output_dir, file_info.fname), 'wb') as f:
            print(f"Creating {file_info.fname}")
            f.write(data[data_ptr+file_info.offset:data_ptr+file_info.offset+file_info.size])


def createPck(dir_path):
    list_path = os.path.join(dir_path, '_list.txt')
    if not os.path.exists(list_path):
        raise ValueError("_list.txt not found")

    with open(list_path, 'rb') as f:
        list_data = f.read().decode('utf-8').strip().replace('\r', '').split('\n')

    fnames_table_sjis = bytearray()
    #fnames = f.read().decode('utf-8').strip().replace('\r', '').split('\n')
    #fnames_table_sjis = bytearray('\r'.join(fnames), 'shift-jis') + b'\r'

    file_entries = []
    for idx, ld in enumerate(list_data):
        fname, ukn5, ukn6 = ld.split(',')
        fname_sjis = fname.encode('shift-jis')
        fnames_table_sjis += fname_sjis + b'\r'

        if idx == 0:
            continue

        fe = FileEntry()
        fe.fname = fname_sjis
        fe.ukn5 = int(ukn5)
        fe.ukn6 = int(ukn6)


        fpath = os.path.join(dir_path, fname)
        if not os.path.exists(fpath):
            raise ValueError(f"{fname} not found")

        with open(fpath, 'rb') as f:
            fe.data = f.read()

        fe.size = len(fe.data)
        if len(file_entries) > 0:
            fe.offset = file_entries[-1].offset + file_entries[-1].size

        file_entries.append(fe)

    ## Create the PCK file
    fname, unk1, unk2 = list_data[0].split(',')

    with open(os.path.join(os.path.dirname(dir_path), fname), 'wb') as f:
        f.write(writeInt32(len(file_entries)+1))
        f.write(writeInt32(len(fnames_table_sjis)))
        f.write(writeInt16(int(unk1))) #unknown
        f.write(writeInt16(int(unk2))) #unknown

        for fe in file_entries:
            f.write(fe.serialize())

        f.write(fnames_table_sjis)

        for fe in file_entries:
            f.write(fe.data)

    print(f'Created {fname}')


def main():
    try:
        for path in argv[1:]:
            try:
                if os.path.isfile(path):
                    print(f'Extracting files from {path}')
                    extractPck(path)
                elif os.path.isdir(path):
                    print(f'Creating pck from {path}')
                    createPck(path)
                else:
                    print(f"{path} doesn't exist")
                
            except ValueError as e:
                print(e)
            
    except KeyboardInterrupt:
        print('Canceling operation')
    except Exception as e:
        print(e)
    finally:
        print('Done')
    
    input("Press Enter to continue...")


if __name__=="__main__":
    main()