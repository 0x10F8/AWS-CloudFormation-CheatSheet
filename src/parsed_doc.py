class AWSRef:

    def __init__(self, ref:str, description:str):
        """
        Initialize the AWSRef object with reference and description.

        Args:
            ref (str): The attribute returned by Ref function.
            description (str): The description of the Ref attribute.
        """
        self.ref = ref
        self.description = description

class ParsedAWSDoc:

    def __init__(self, resource_name:str, ref:str, getatt:list[AWSRef]):
        """
        Initialize the ParsedAWSDoc object with resource name, reference, and getatt.

        Args:
            resource_name (str): The name of the AWS resource.
            ref (str): The attribute returned by Ref function.
            getatt (list[AWSRef]): The attributes available for the GetAtt function.
        """
        self.resource_name = resource_name
        self.ref = ref
        self.getatt = getatt