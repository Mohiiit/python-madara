import hashlib

def file_checksum(file_path):
    """Generate a checksum for a file."""
    hash_algo = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def compare_files(file1_path, file2_path):
    """Compare two files to check if they are the same."""
    return file_checksum(file1_path) == file_checksum(file2_path)

# Replace 'file1.txt' and 'file2.txt' with your actual file paths
file1 = '/Users/mohitdhattarwal/Desktop/madara-internship/recover-blobs/state_diff_639404.txt'
file2 = '/Users/mohitdhattarwal/Desktop/madara-internship/madara-orch-test/test_blob_ 639404.txt'

def read_file_to_array(file_path):
    """Read a file and store its lines in an array."""
    with open(file_path, 'r') as file:
        return file.readlines()

def compare_arrays(array1, array2):
    """Compare two arrays to check if they are the same."""
    return array1 == array2
# Check if the files are the same
# if compare_files(file1, file2):
#     print("The files are the same.")
# else:
#     print("The files are different.")
    
lines_file1 = read_file_to_array(file1)
lines_file2 = read_file_to_array(file2)
print(lines_file1, lines_file2)
if compare_arrays(lines_file1, lines_file2):
    print("The files have the same content.")
else:
    print("The files have different content.")