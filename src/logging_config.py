import logging
import sys

# Don't know why, but logging stopped working suddenly before we added this
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.DEBUG,  # or DEBUG for detailed logs during development
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
