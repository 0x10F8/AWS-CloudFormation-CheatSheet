from bs4 import BeautifulSoup
import requests
from parsed_doc import ParsedAWSDoc, AWSRef

class AWSDocsParser:
    """
    A class to parse AWS documentation pages to extract resource names, references, and attributes.
    """
    
    def __init__(self):
        """
        Initialize the AWSDocsParser object.
        """
        pass

    def download_aws_doc(self, url: str) -> str:
        """
        Download the AWS documentation from the given URL.
        
        Args:
            url (str): The URL of the AWS documentation page to download.
            
        Returns:
            str: The HTML content of the downloaded page.
        """
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to download page: {response.status_code}")
    

    def parse_aws_doc(self, html_content: str) -> ParsedAWSDoc:
        """
        Parse the AWS documentation HTML content to extract resource name, reference, and getatt.
        
        Args:
            html_content (str): The HTML content of the AWS documentation page.
            
        Returns:
            ParsedAWSDoc: An object containing the parsed information.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        # Parse the resource name from the title tag
        page_title = soup.find('title').text.strip()
        resource_name = page_title.split(" ")[0]  # Assuming the first word is the resource name
        # Parse the getatt attributes   
        attributes_html = soup.find_all('div', class_='variablelist')
        getatt = []
        for attributes in attributes_html:
            if "getatt" in str(attributes):
                codes = attributes.find_all('code', class_='code')
                ps = attributes.find_all('dd')
                get_att_codes = [code.text for code in codes if code.parent.name == 'span']
                get_att_descriptions = [p.text.strip().replace("  ", "").replace("\n", " ") for p in ps]
                if len(get_att_codes) <= len(get_att_descriptions):
                    for i in range(len(get_att_codes)):
                        getatt.append(AWSRef(get_att_codes[i], get_att_descriptions[i]))
                else:
                    raise Exception("Mismatch between getatt codes and descriptions")
        # Parse the main body content to find the Ref function
        main_body_col = soup.find("div", id="main-col-body")
        ref_content = ""
        on_ref_content = False
        for html_block in main_body_col:
            if ">Fn::GetAtt</h3>" in str(html_block):
                on_ref_content = False
            if ">Ref</h3>" in str(html_block):
                on_ref_content = True
            if on_ref_content:
                ref_content += str(html_block)
        soup = BeautifulSoup(ref_content, 'html.parser')
        ref_p = soup.find_all('p')
        ref = ""
        for p in ref_p:
            ref += str(p)
        return ParsedAWSDoc(resource_name, ref, getatt)

"""
parser = AWSDocsParser()
with open("example.html") as f:
    html_content = f.read()
    parsed_doc = parser.parse_aws_doc(html_content)
    print(parsed_doc.resource_name)
    print(parsed_doc.ref)
    for attr in parsed_doc.getatt:
        print(f"Ref: {attr.ref}, Description: {attr.description}")
"""