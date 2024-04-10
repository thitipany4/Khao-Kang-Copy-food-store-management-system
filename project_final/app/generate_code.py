import random
import string
from .models import Order
def generate_random_system_code(length=6):
        while True:
            random_numbers = ''.join(random.choices(string.digits, k=length//2))
            random_letters = ''.join(random.choices(string.ascii_uppercase, k=length//2))
            combined_string = random_numbers + random_letters
            shuffled_code = ''.join(random.sample(combined_string, len(combined_string)))
            if not Order.objects.filter(ref_code=shuffled_code).exists():
                return shuffled_code