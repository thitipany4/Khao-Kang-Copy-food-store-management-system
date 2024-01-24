import random
import string
from .models import Order
def generate_random_system_code(length=6):
    # Generate random numbers and letters
        while True:
            # Generate random numbers and letters
            random_numbers = ''.join(random.choices(string.digits, k=length//2))
            random_letters = ''.join(random.choices(string.ascii_uppercase, k=length//2))

            # Shuffle the combined string
            combined_string = random_numbers + random_letters
            shuffled_code = ''.join(random.sample(combined_string, len(combined_string)))

            # Check if the code is unique
            if not Order.objects.filter(ref_code=shuffled_code).exists():
                return shuffled_code