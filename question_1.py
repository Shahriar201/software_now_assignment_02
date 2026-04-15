import os

def shift_char(char, shift_amount):
    """Helper function to shift a character within its alphabet case."""
    if 'a' <= char <= 'z':
        start = ord('a')
        # Ensure the shift wraps correctly within 26 letters
        return chr((ord(char) - start + shift_amount) % 26 + start)
    elif 'A' <= char <= 'Z':
        start = ord('A')
        return chr((ord(char) - start + shift_amount) % 26 + start)
    return char

def encrypt_file(input_file, output_file, s1, s2):
    """Encrypts the file based on the specific shift rules."""
    try:
        with open(input_file, 'r') as f:
            content = f.read()
        
        encrypted_chars = []
        for char in content:
            if 'a' <= char <= 'm':
                encrypted_chars.append(shift_char(char, s1 * s2))
            elif 'n' <= char <= 'z':
                encrypted_chars.append(shift_char(char, -(s1 + s2)))
            elif 'A' <= char <= 'M':
                encrypted_chars.append(shift_char(char, -s1))
            elif 'N' <= char <= 'Z':
                encrypted_chars.append(shift_char(char, s2**2))
            else:
                encrypted_chars.append(char)
        
        encrypted_text = "".join(encrypted_chars)
        with open(output_file, 'w') as f:
            f.write(encrypted_text)
        print(f"File encrypted successfully: {output_file}")
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
    except Exception as e:
        print(f"An error occurred during encryption: {e}")

def decrypt_file(input_file, output_file, s1, s2):
    """Decrypts by checking which original range the character must have come from."""
    try:
        with open(input_file, 'r') as f:
            content = f.read()
            
        decrypted_chars = []
        for char in content:
            if 'a' <= char <= 'z':
                # Reversing first half (a-m) rule: -(s1*s2)
                orig_am = shift_char(char, -(s1 * s2))
                # Reversing second half (n-z) rule: +(s1+s2)
                orig_nz = shift_char(char, (s1 + s2))
                
                # IMPORTANT: Check if the reversed char matches its original range
                if 'a' <= orig_am <= 'm':
                    decrypted_chars.append(orig_am)
                elif 'n' <= orig_nz <= 'z':
                    decrypted_chars.append(orig_nz)
                else:
                    # Fallback if wrapping causes overlap
                    decrypted_chars.append(orig_am)
                    
            elif 'A' <= char <= 'Z':
                # Reversing first half (A-M) rule: +s1
                orig_am_upper = shift_char(char, s1)
                # Reversing second half (N-Z) rule: -(s2^2)
                orig_nz_upper = shift_char(char, -(s2**2))
                
                if 'A' <= orig_am_upper <= 'M':
                    decrypted_chars.append(orig_am_upper)
                elif 'N' <= orig_nz_upper <= 'Z':
                    decrypted_chars.append(orig_nz_upper)
                else:
                    decrypted_chars.append(orig_am_upper)
            else:
                decrypted_chars.append(char)

        decrypted_text = "".join(decrypted_chars)
        with open(output_file, 'w') as f:
            f.write(decrypted_text)
        print(f"File decrypted successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred during decryption: {e}")

def verify_decryption(original_file, decrypted_file):
    """Compares the original and decrypted files."""
    try:
        with open(original_file, 'r') as f1, open(decrypted_file, 'r') as f2:
            if f1.read() == f2.read():
                print("Verification: SUCCESS! The files match.")
            else:
                print("Verification: FAILED! The files do not match.")
    except Exception as e:
        print(f"An error occurred during verification: {e}")

def main():
    # Setup for the provided raw_text.txt
    raw_filename = "raw_text.txt"
    
    try:
        shift1 = int(input("Enter shift1 value: "))
        shift2 = int(input("Enter shift2 value: "))
        
        encrypt_file(raw_filename, "encrypted_text.txt", shift1, shift2)
        decrypt_file("encrypted_text.txt", "decrypted_text.txt", shift1, shift2)
        verify_decryption(raw_filename, "decrypted_text.txt")
        
    except ValueError:
        print("Invalid input. Please enter integer values for shifts.")

if __name__ == "__main__":
    main()