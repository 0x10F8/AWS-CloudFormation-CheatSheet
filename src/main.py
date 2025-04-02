from aws_docs_updater import AWSDocsUpdater
from create_html_table import HTMLTableGenerator
from datetime import datetime

if __name__ == "__main__":
    updater = AWSDocsUpdater()
    if updater.detect_changes():
        print("Changes detected in AWS documentation. Updating...")
        updater.update_missing_services()
        print("Update completed.")
        # Generate the HTML table
        print("Generating HTML table...")
        html_table_generator = HTMLTableGenerator()
        html_table_generator.create_html_table(updater.OUTPUT_DIR)
        updater.update_meta_data(datetime.now())
