from doc_crawler import AWSDocsCrawler
from parse_aws_doc import AWSDocsParser
import os
import json

def main():
    """
    Main function to crawl AWS documentation and parse it.
    """
    # Initialize the crawler and parser
    crawler = AWSDocsCrawler()
    parser = AWSDocsParser()

    output_dir = "output"
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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
            output_file = os.path.join(output_dir, output_file_name)
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


if __name__ == "__main__":
    main()