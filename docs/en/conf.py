###############
# Qiyas Sadıqov CC
###############

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_common"))

from shared import configure

configure(globals(), "en")
