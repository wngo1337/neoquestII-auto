import logging

# Don't know why, but logging stopped working suddenly before we added this
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for detailed logs during development
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
