import os 
import json

# iterate through json files in output directory
# and create an HTML table with the contents of each file
def create_html_table(output_dir):
    """
    Create an HTML table from JSON files in the output directory.
    """
    # Initialize the HTML table
    html_table = """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>AWS CloudFormation Ref & GetAtt Cheat Sheet</title>
        <style>
            * {
                -webkit-box-sizing: border-box;
                -moz-box-sizing: border-box;
                box-sizing: border-box;
            }
            .brand-title {
                margin: 0;
                position: relative;
                text-align: center;
                font-size: 2.5em;
            }
        </style>
    </head>
    <body>
        <h1 class="brand-title">AWS CloudFormation Ref & GetAtt Cheat Sheet</h1>
        <table class="pure-table pure-table-bordered" style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
        <thead>
            <tr>
                <th>Resource Name</th>
                <th>Ref</th>
                <th>GetAtt</th>
            </tr>
        </thead>
        <tbody>
    """

    # Iterate through each JSON file in the output directory
    for filename in os.listdir(output_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(output_dir, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)
                resource_name = data.get("ResourceName")
                ref = data.get("Ref", "N/A")
                getatt = "N/A"
                if "GetAtt" in data:
                    # If GetAtt is a list of dictionaries, extract the Ref and Description
                    if isinstance(data["GetAtt"], list) and len(data["GetAtt"]) > 0:
                        # Extract the Ref and Description from each dictionary in the list
                        getatt = "<ul>"
                        for attr in data["GetAtt"]:
                            getatt += f"<li><b>{attr['Ref']}</b>\t-\t{attr['Description']}</li>"
                        getatt += "</ul>"
                # Add a row to the HTML table
                html_table += f"""
                    <tr>
                        <td>{resource_name}</td>
                        <td>{ref}</td>
                        <td>{getatt}</td>
                    </tr>
                """

    # Close the HTML table
    html_table += """
        </tbody>
        </table>
    </body>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/purecss@3.0.0/build/pure-min.css" integrity="sha384-X38yfunGUhNzHpBaEBsWLO+A0HDYOQi8ufWDkZ0k9e0eXz/tH3II7uKZ9msv++Ls" crossorigin="anonymous">
    </html>
    """

    # Write the HTML table to a file
    with open("docs/index.html", 'w', encoding="utf8") as f:
        f.write(html_table)

if __name__ == "__main__":
    create_html_table("output")
