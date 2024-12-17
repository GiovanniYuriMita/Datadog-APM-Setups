import time
import logging
from ddtrace import tracer, patch_all
from ddtrace.debugging import DynamicInstrumentation

DynamicInstrumentation.enable()

# Enable Datadog auto-instrumentation
patch_all()

# Configure logging
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Function to create and log custom spans
def create_custom_span():
    with tracer.trace("custom.span", service="bw-python") as span:
        span.set_tag("abc", "123")
        log.info("Custom span created")

class CustomClass:
    def __init__(self, name):
        self.name = name

    def process_data(self, data):
        log.info(f"Processing data: {data}...")
        processed_data = data.upper()
        log.info(f"Processed data: {processed_data}")
        return processed_data

    def calculate(self, a, b):
        log.info(f"Calculating the sum of {a} and {b}")
        result = a + b
        log.info(f"Calculation result: {result}")
        return result

def main():
    print("Hello!\nThis is a simple Python App Designed by BW Soluções to show Datadog features.")
    custom_obj = CustomClass("ExampleClass")

    while True:
        create_custom_span()
        custom_obj.process_data("sample data")
        custom_obj.calculate(2, 2)
        time.sleep(3)

if __name__ == "__main__":
    main()