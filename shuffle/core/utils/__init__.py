import random
import string

def alpha(): 
    return ''.join(
        random.choice(
            string.ascii_uppercase + 
            string.ascii_lowercase + 
            string.digits
        ) 
        for _ in range(16)
    ).lower()

from .email import *
from .helpers import *
from .json import *
from .oauth import *