
from doc_crawler import AWSDocsCrawler
from parse_aws_doc import AWSDocsParser
import os
import json
from xml.etree import ElementTree
import tempfile
import requests
from datetime import datetime
import re

class AWSDocsUpdater:
    """
    A class to update AWS documentation by checking for changes in the release notes
    and parsing the documentation for missing services.
    """
    
    # RSS feed URL for AWS CloudFormation release notes
    RELEASE_RSS_URL = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-cloudformation-release-notes.rss"

    # Meta file name
    META_FILE = "meta.json"

    # Regex pattern to match AWS service names
    AWS_SERVICE_REGEX = r"AWS::[a-zA-Z0-9]+::[a-zA-Z0-9]+"

    # Output directory for parsed documents
    OUTPUT_DIR = "output"

    def _load_meta_data(self) -> dict:
        """
        Load the meta data from the meta.json file.
        Returns:
            dict: The meta data loaded from the file.
        """
        if os.path.exists(self.META_FILE):
            with open(self.META_FILE, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"Meta file {self.META_FILE} not found.")

    def _get_last_update_time(self) -> datetime:
        """
        Get the last update time from the meta data.
        Returns:
            datetime: The last update time.
        """
        meta_data = self._load_meta_data()
        last_update_time = meta_data.get("last_update_time")
        if last_update_time:
            return datetime.strptime(last_update_time, "%Y-%m-%dT%H:%M:%S")
        else:
            return None


    def _get_services_changed_since(self, rss_file: tempfile.NamedTemporaryFile, last_update_time: datetime) -> set:
        """
        Parse the RSS feed and check for changes in services since the last update time.
        Args:
            rss_file (tempfile.NamedTemporaryFile): Temporary file containing the RSS feed.
            last_update_time (datetime): The last update time to compare against.
            Returns:
                set: A set of services that have changed since the last update time.
        """
         # Parse the XML file
        xml_tree = ElementTree.parse(rss_file.name)
        root = xml_tree.getroot()

        # Initialize a set to store changed services
        changed_services = set()

        # Iterate through each item in the RSS feed
        for item in root.findall('./channel/item'): 
            description = item.find('description').text
            pub_date = item.find('pubDate').text
            # Parse the publication date
            pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            # Check if the publication date is newer than the last update time
            
            if pub_date > last_update_time:
                found_service_changes = re.findall(self.AWS_SERVICE_REGEX, description)
                if found_service_changes:
                    for service in found_service_changes:
                        changed_services.add(service)
        return changed_services
    
    def update_meta_data(self, last_update_time: datetime):
        """
        Update the meta data with the last update time.
        Args:
            last_update_time (datetime): The last update time to save.
        """
        meta_data = {
            "last_update_time": last_update_time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        with open(self.META_FILE, 'w') as f:
            json.dump(meta_data, f, indent=4)

    def detect_changes(self):
        """
        Parse RSS xml in URL
        Check if there are any changes in the release notes
        Remove the output file for the service if it has changed.
        """
        changes = False
        # Load the last update time from the meta.json file
        last_update_time = self._get_last_update_time()
        
        # Create a tmp file to hold the downloaded RSS feed
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            # Download the RSS feed
            tmp_file.write(requests.get(self.RELEASE_RSS_URL).content)
            # Parse the RSS feed and get any changed services
            changed_services = self._get_services_changed_since(tmp_file, last_update_time)
            if changed_services:
                changes = True
                print(f"Changed services since last update: {changed_services}")
                # Remove the output files for the changed services
                for service in changed_services:
                    output_file_name = service.lower().replace("aws", "aws-resource").replace("::", "-") + ".json"
                    output_file = os.path.join(self.OUTPUT_DIR, output_file_name)
                    if os.path.exists(output_file):
                        os.remove(output_file)
                        print(f"Removed output file: {output_file}")
                    else:
                        print(f"Output file for service {service} not found - {output_file}")
            else:
                print("No changes detected since last update.")
        finally:
            # Close the temporary file and delete it
            tmp_file.close()
            os.unlink(tmp_file.name)
        return changes


    def update_missing_services(self):
        """
        Crawl AWS documentation and parse it.
        This function will only process services that are missing in the output directory.
        """
        # Initialize the crawler and parser
        crawler = AWSDocsCrawler()
        parser = AWSDocsParser()

        # Create the output directory if it doesn't exist
        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)

        # Get all service links
        service_links = crawler.get_all_service_links()
        print(f"Found {len(service_links)} service links.")

        # Iterate through each service link and parse the documentation
        for service_link in service_links:
            print(f"Processing service link: {service_link}")
            resource_links = crawler.get_resource_links_for_service(service_link)
            print(f"Found {len(resource_links)} resource links for service {service_link}.")
            for resource_link in resource_links:
                # Prepare output file
                output_file_name = resource_link.split("/")[-1].replace(".html", ".json")
                output_file = os.path.join(self.OUTPUT_DIR, output_file_name)
                # Check if the file already exists
                if os.path.exists(output_file):
                    print(f"File {output_file} already exists. Skipping.")
                    continue
                
                # Download the AWS documentation page and parse it
                print(f"Processing resource link: {resource_link}")
                html_content = parser.download_aws_doc(resource_link)
                parsed_doc = parser.parse_aws_doc(html_content)
                print(f"Parsed document for resource: {parsed_doc.resource_name}")
                
                # Save the parsed document to a JSON file
                json_object = {
                    "ResourceName": parsed_doc.resource_name,
                    "Ref": parsed_doc.ref,
                    "GetAtt": [{"Ref": attr.ref, "Description": attr.description} for attr in parsed_doc.getatt]
                }
                with open(output_file, 'w') as f:
                    f.write(json.dumps(json_object, indent=4))
                print(f"Saved parsed document to {output_file}")