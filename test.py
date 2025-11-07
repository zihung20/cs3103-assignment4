# generate_text_file.py

def generate_text_file(filename="./test/output.txt", min_size=50000):
    with open(filename, "w") as f:
        line_number = 1
        total_bytes = 0

        while total_bytes < min_size:
            line = f"{line_number}: This is a sample line of text to fill the file.\n"
            f.write(line)
            total_bytes += len(line.encode("utf-8"))
            line_number += 1

    print(f"File '{filename}' created with size {total_bytes} bytes and {line_number - 1} lines.")

if __name__ == "__main__":
    generate_text_file()
