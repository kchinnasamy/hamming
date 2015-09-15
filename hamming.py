import sys

class Hamming(object):

    def bits(self, f):
        bytes_data = (ord(b) for b in f.read())
        for b in bytes_data:
            for i in reversed(xrange(8)):
                yield (b >> i) & 1

    def get_hamming(self, binary_str):
        """Given binary string (e.g., "0101"), compute the hamming.
           https://en.wikipedia.org/wiki/Hamming_code
           Ignore the 8th bit (most significant bit) in the character.
           Return an str: '0' or '1'.
        """
        self.haming_parity_bits = [1, 2, 4, 8]
        pos_binarypos_map = [(1, [3, 5, 7, 9, 11]), (2, [3, 6, 7, 10, 11]), (4, [5, 6, 7, 12]), (8, [9, 10, 11, 12])]
        if len(binary_str) != 12:
            hamming_code = [0, 0, int(binary_str[0]), 0, int(binary_str[1]), int(binary_str[2]), int(binary_str[3]), 0, int(binary_str[4]), int(binary_str[5]), int(binary_str[6]), int(binary_str[7])]
        else:
            hamming_code = map(lambda x: int(x), binary_str)
        for (pos, binarypos) in pos_binarypos_map:
            total = 0
            for bpos in binarypos:
                total += hamming_code[bpos - 1]
            hamming_code[pos - 1] = (total % 2)  
        hamming_code = reduce(lambda x, y: x + str(y), hamming_code, '')
        return hamming_code

    def get_ascii(self, byte_str):
        """Get ASCII character from a binary string."""
        value = int(byte_str, 2)
        return chr(value)


class HammingEncoder(Hamming):

    def encode(self, text):
        """Return the hamming encoded version of the text string."""

        encode_list = []
        for c in text:
            # Get binary string representation of c
            binary_str = "{0:08b}".format(ord(c))
            # Remove 8th bit
            # binary_str = binary_str[1:]
            hamming = self.get_hamming(binary_str)
            encode_list += str(hamming)

        encoded_text = ''.join(encode_list)
        return encoded_text


class HammingFileEncoder(HammingEncoder):

    def __init__(self, in_filename, out_filename):
        self.in_filename = in_filename
        self.out_filename = out_filename

    def encode_ascii_file(self):
        if self.out_filename is None:
            with open(self.in_filename) as infile:
                for line in infile:
                    encoded_text = self.encode(line)
                    print encoded_text
        else:
            outfile = open(self.out_filename, 'w')
            with open(self.in_filename) as infile:
                for line in infile:
                    encoded_text = self.encode(line)
                    outfile.write(encoded_text)
            outfile.close()

    def encode_bin_file(self):
        if self.out_filename is None:
            with open(self.in_filename) as infile:
                for line in infile:
                    encoded_text = self.encode(line)
                    bin_array = ''.join([chr(int(encoded_text[index * 8: index * 8 + 8], base=2)) for index in range(len(encoded_text) / 8)])
                    print bin_array
        else:
            outfile = open(self.out_filename, 'wb')
            with open(self.in_filename) as infile:
                for line in infile:
                    encoded_text = self.encode(line)
                    bin_array = ''.join([chr(int(encoded_text[index * 8: index * 8 + 8], base=2)) for index in range(len(encoded_text) / 8)])
                    outfile.write(bin_array)
            outfile.close()

class HammingDecoder(Hamming):

    def decode_ascii(self, hamming_code):
        """Return decoded hamming_code as a string."""

        out_string = ''

        while len(hamming_code) > 0:
            if hamming_code[0] == '\n':
                break
            byte_str = hamming_code[0:12]
            # Removing the hamming encoding bits
            byte_str = byte_str[2] + byte_str[4] + byte_str[5] + byte_str[6] + byte_str[8] + byte_str[9] + byte_str[10] + byte_str[11]  
            hamming_code = hamming_code[12:]
            out_string += self.get_ascii(byte_str)
        return out_string



class HammingFileDecoder(HammingDecoder):

    def __init__(self, in_filename, out_filename):
        self.in_filename = in_filename
        self.out_filename = out_filename

    def decode_ascii_file(self):
        if self.out_filename is None:
            with open(self.in_filename) as infile:
                for line in infile:
                    decoded_text = self.decode_ascii(line)
                    print decoded_text
        else:    
            outfile = open(self.out_filename, 'w')
            with open(self.in_filename) as infile:
                for line in infile:
                    decoded_text = self.decode_ascii(line)
                    outfile.write(decoded_text)
            outfile.close()

    def decode_bin_file(self):
        tmp = ""
        for b in self.bits(open(self.in_filename, 'rb')):
            tmp += str(b)
        if self.out_filename == None:
            print self.decode_ascii(tmp)
        else:
            outfile = open(self.out_filename, 'w')
            outfile.write(self.decode_ascii(tmp))
            outfile.close()
        

class HammingChecker(Hamming):

    def check(self, text):
        """Check the Hamming of an encoded file.
           Return a list of byte positions with bad bit.
        """
        positions = []
        set_id = 0
        while len(text) > 0:
            if text[0] == '\n':
                break
            byte_str = text[0:12]

            # Extract the bytes
            check_hamming = self.get_hamming(byte_str)
            temp_pos = 0
            for bit in self.haming_parity_bits:
                if byte_str[bit - 1] != check_hamming[bit - 1]:
                    temp_pos += bit
            if temp_pos != 0:
                positions.append((12 * set_id) + temp_pos)
            text = text[12:]
            set_id += 1
        return positions

class HammingFileChecker(HammingChecker):

    def __init__(self, in_filename):
        self.in_filename = in_filename

    def check_ascii_file(self):
        line_no = 1
        positions = []
        with open(self.in_filename) as infile:
            for line in infile:
                err_pos = self.check(line)
                if len(err_pos) != 0:   
                    positions.append((line_no, err_pos))
                line_no += 1
        return positions
    
    def check_bin_file(self):
        tmp = ""
        for b in self.bits(open(self.in_filename, 'rb')):
            tmp += str(b)
        
        return self.check(tmp)
        
    
class HammingFixer(HammingChecker):

    def fix(self, text):
        """Check the parity of an encoded file.
           Return a list of byte positions with bad parity.
        """
        positions = self.check(text)
        for pos in positions:
            fix_bit = "0"
            index = pos - 1
            if text[index] == "0":
                fix_bit = "1"
            text = text[:index] + fix_bit + text[index + 1:]
        return text

class HammingFileFixer(HammingFixer):
    def __init__(self, in_filename, out_filename):
        self.in_filename = in_filename
        self.out_filename = out_filename

    def fix_ascii_file(self):
        outfile = open(self.out_filename, 'w')
        with open(self.in_filename) as infile:
            for line in infile:
                fixed_hamming = self.fix(line)
                outfile.write(fixed_hamming)
        outfile.close()

    def fix_bin_file(self):
        outfile = open(self.out_filename, 'wb')
        tmp = ""
        for b in self.bits(open(self.in_filename, 'rb')):
            tmp += str(b)
        fixed_hamming = self.fix(tmp)
        bin_array = ''.join([chr(int(fixed_hamming[index * 8: index * 8 + 8], base=2)) for index in range(len(fixed_hamming) / 8)])
        outfile.write(bin_array)
        outfile.close()

    
class HammingError(Hamming):

    def error(self, text, pos):    
        err_bit = "0"
        index = pos - 1
        if text[index] == "0":
            err_bit = "1"
        text = text[:index] + err_bit + text[index + 1:]
        return text

class HammingFileError(HammingError):
    def __init__(self, in_filename, out_filename, err_line_no, pos):
        self.in_filename = in_filename
        self.out_filename = out_filename
        self.err_line_no = int(err_line_no)
        self.err_pos = int(pos)

    def error_ascii_file(self):
        line_no = 1
        outfile = open(self.out_filename, 'w')
        with open(self.in_filename) as infile:
            for line in infile:
                err_hamming = line
                if line_no == self.err_line_no:
                    err_hamming = self.error(line, self.err_pos)
                outfile.write(err_hamming)
                line_no += 1 
        outfile.close()
        
    def error_bin_file(self):
        
        tmp = "" 
        for b in self.bits(open(self.in_filename, 'rb')):
            tmp += str(b)
        err_hamming = ""
        line_no = 1
        if line_no == self.err_line_no:
            err_hamming = self.error(tmp, self.err_pos)
        outfile = open(self.out_filename, 'wb')
        bin_array = ''.join([chr(int(err_hamming[index * 8: index * 8 + 8], base=2)) for index in range(len(err_hamming) / 8)])
        outfile.write(bin_array)
        outfile.close()


if __name__ == '__main__':
    
    _type = sys.argv[1]
    cmd = sys.argv[2]
    input_file = sys.argv[3]
    output_file = None
    
    if len(sys.argv) == 5:
        output_file = sys.argv[4]

    if cmd == 'enc':        
        encoder = HammingFileEncoder(input_file, output_file)
        if _type == 'asc':
            encoder.encode_ascii_file()
        else:
            encoder.encode_bin_file()

    elif cmd == 'dec':
        decoder = HammingFileDecoder(input_file, output_file)
        if _type == 'asc':  
            decoder.decode_ascii_file()
        else:
            decoder.decode_bin_file()    

    elif cmd == 'chk':
        checker = HammingFileChecker(input_file)
        if _type == 'asc':
            positions = checker.check_ascii_file()
        else:
            positions = checker.check_bin_file()
            
        if positions:
            print("Bad byte positions (Line No. , Positions list):")
            print(positions)
        else:
            print("Vaild Input.")

    elif cmd == 'fix':
        fixer = HammingFileFixer(input_file, output_file)
        if _type == 'asc':
            fixer.fix_ascii_file()
        else:
            fixer.fix_bin_file()
            
    elif cmd == 'err':
        if len(sys.argv) == 6:
            line = 1  
            pos = sys.argv[3]
            input_file = sys.argv[4]
            output_file = sys.argv[5]
        else:    
            line = sys.argv[3]  
            pos = sys.argv[4]
            input_file = sys.argv[5]
            output_file = sys.argv[6]
        err = HammingFileError(input_file, output_file, line, pos)
        if _type == 'asc':
            err.error_ascii_file()
        else:
            err.error_bin_file()

