import requests
from bs4 import BeautifulSoup

class AWSDocsCrawler:

    base_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html"

    def get_all_service_links(self) -> list[str]:
        """
        Get all the service links from the AWS documentation page.
        
        Returns:
            list[str]: A list of URLs for each AWS service documentation page.
        """
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        resource_links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            print(href)
            if href and "./AWS_" in href:
                # Construct the full URL
                full_url = f"https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/{href}"
                resource_links.append(full_url)
        return resource_links
    

    def get_resource_links_for_service(self, service_url:str) -> list[str]:
        """
        Get all the resource links for a specific AWS service.
        
        Args:
            service_url (str): The URL of the AWS service documentation page.
            
        Returns:
            list[str]: A list of URLs for each resource in the specified AWS service.
        """
        response = requests.get(service_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        resource_links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and "./aws-resource-" in href:
                # Construct the full URL
                full_url = f"https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/{href}"
                resource_links.append(full_url)
        return resource_links