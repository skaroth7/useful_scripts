import requests
import csv
import xml.etree.ElementTree as ET
import concurrent.futures

def fetch_hgnc_from_ensembl(ensembl_id):
    try:
        headers = {"content-type": "application/json"}
        url = f"https://rest.ensembl.org/lookup/id/{ensembl_id}?expand=1"
        response = requests.get(url, headers=headers)
        data = response.json()
        return ensembl_id, data.get("display_name", "No result")
    except Exception as e:
        return ensembl_id, f"Error: {e}"

def get_hgnc_symbol(identifier):
    identifier = identifier.strip()
    if "ENST" in identifier:
        return fetch_hgnc_from_ensembl(identifier)
    else:
        return fetch_hgnc_from_uniprot(identifier)

def fetch_hgnc_from_uniprot(uniprot_id):
    try:
        url = f"https://www.uniprot.org/uniprot/{uniprot_id}.xml"
        response = requests.get(url)
        
        if response.status_code != 200:
            return uniprot_id, "No result"
        
        root = ET.fromstring(response.content)
        
        # Namespace dictionary for XML parsing
        ns = {'uniprot': 'http://uniprot.org/uniprot'}
        
        # Extract HGNC gene name from XML content
        gene_name_element = root.find('.//uniprot:gene/uniprot:name[@type="primary"]', namespaces=ns)
        if gene_name_element is not None:
            return uniprot_id, gene_name_element.text
        else:
            return uniprot_id, "No result"
    except Exception as e:
        return uniprot_id, f"Error: {e}"

def get_hgnc_symbol(identifier):
    identifier = identifier.strip()
    if "ENST" in identifier:
        return fetch_hgnc_from_ensembl(identifier)
    else:
        return fetch_hgnc_from_uniprot(identifier)

if __name__ == "__main__":
    input_filename = "ids.txt"
    output_filename = "output.csv"
    results = {}

    with open(input_filename, 'r') as input_file:
        identifiers = [line.strip() for line in input_file]

    # Using 16 threads to fetch HGNC symbols
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        for identifier, symbol in executor.map(get_hgnc_symbol, identifiers):
            results[identifier] = symbol

    with open(output_filename, 'w') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(['ID', 'HGNC Symbol'])
        for identifier, symbol in results.items():
            writer.writerow([identifier, symbol])
