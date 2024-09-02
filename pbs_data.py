import datetime
import requests
import csv
from io import StringIO
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datasets import Dataset

class PBSPublicDataAPIClient:
    def __init__(self, subscription_key, base_url='https://data-api.health.gov.au/pbs/api/v3', rate_limit=0.2):
        self.subscription_key = subscription_key
        self.base_url = base_url
        self.rate_limit = rate_limit  # Requests per second
        self.last_request_time = 0
        
        # Set up a session with retry strategy
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def get_sample_data(self, endpoint, limit=5):
        params = {"limit": limit}
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def fetch_sample_data(self):
        schedules = self.get_schedules()
        latest_schedule = schedules[0]['schedule_code']

        endpoints = [
            "amt-items",
            "atc-codes",
            "indications",
            "prescribing-texts",
            "item-prescribing-text-relationships",
            "restrictions",
            "item-restriction-relationships"
        ]

        sample_data = {}
        for endpoint in endpoints:
            print(f"Fetching sample data from /{endpoint}...")
            data = self.get_sample_data(endpoint)
            if data:
                sample_data[endpoint] = data
                print(f"Sample keys for {endpoint}: {data[0].keys()}")
            else:
                print(f"No data found for {endpoint}")
            time.sleep(2)  # Wait 2 seconds between requests to avoid rate limiting

        return sample_data

    def get_raw_data(self, endpoint, params=None, accept="application/json"):
        response = self.make_request(endpoint, params=params, accept=accept)
        return response.text

    def make_request(self, endpoint, params=None, accept="application/json"):
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "subscription-key": self.subscription_key,
            "Accept": accept
        }

        while True:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < 1 / self.rate_limit:
                sleep_time = (1 / self.rate_limit) - time_since_last_request
                time.sleep(sleep_time)

            try:
                response = self.session.get(url, headers=headers, params=params)
                self.last_request_time = time.time()

                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    print(f"Rate limit exceeded. Waiting for {retry_after} seconds.")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                print(f"Request failed: {str(e)}. Retrying in 5 seconds...")
                time.sleep(5)

    def get_schedules(self, limit=100):
        endpoint = "schedules"
        params = {"limit": limit}
        response = self.make_request(endpoint, params=params)
        json_data = response.json()
        return json_data['data']

    def get_amt_items(self, schedule_code, limit=100000):
        endpoint = "amt-items"
        params = {
            "schedule_code": schedule_code,
            "limit": limit
        }
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def get_atc_codes(self, schedule_code, limit=100000):
        endpoint = "atc-codes"
        params = {
            "schedule_code": schedule_code,
            "limit": limit
        }
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def get_indications(self, schedule_code, limit=100000):
        endpoint = "indications"
        params = {
            "schedule_code": schedule_code,
            "limit": limit
        }
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def get_prescribing_texts(self, schedule_code, limit=100000):
        endpoint = "prescribing-texts"
        params = {
            "schedule_code": schedule_code,
            "limit": limit
        }
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def get_item_prescribing_text_relationships(self, schedule_code, limit=100000):
        endpoint = "item-prescribing-text-relationships"
        params = {
            "schedule_code": schedule_code,
            "limit": limit
        }
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def get_restrictions(self, schedule_code, limit=100000):
        endpoint = "restrictions"
        params = {
            "schedule_code": schedule_code,
            "limit": limit
        }
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def get_item_restriction_relationships(self, schedule_code, limit=100000):
        endpoint = "item-restriction-relationships"
        params = {
            "schedule_code": schedule_code,
            "limit": limit
        }
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def get_restriction_prescribing_text_relationships(self, schedule_code, limit=100000):
        endpoint = "restriction-prescribing-text-relationships"
        params = {
            "schedule_code": schedule_code,
            "limit": limit
        }
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def get_items(self, schedule_code, limit=100000):
        endpoint = "items"
        params = {
            "schedule_code": schedule_code,
            "limit": limit
        }
        response = self.make_request(endpoint, params=params, accept="text/csv")
        csv_content = StringIO(response.text)
        return list(csv.DictReader(csv_content))

    def fetch_rheumatology_biologics_data(self):
        biologics = [
            "adalimumab", "etanercept", "infliximab", "certolizumab", "golimumab",
            "rituximab", "abatacept", "tocilizumab", "secukinumab", "ixekizumab",
            "ustekinumab", "guselkumab", "tofacitinib", "baricitinib", "secukinumab",
            "upadacitinib", "anifrolumab"
        ]

        rheumatic_diseases = [
            "rheumatoid arthritis", "psoriatic arthritis", "ankylosing spondylitis",
            "non-radiographic axial spondyloarthritis", "giant cell arteritis", 
            "juvenile idiopathic arthritis", "systemic lupus erythematosus"
        ]

        data = {}
        schedules = self.get_schedules()

        # Select schedule based on current month
        current_date = datetime.datetime.now()
        current_schedule = next(
            (s for s in schedules if s['effective_year'] == current_date.year and s['effective_month'] == current_date.strftime('%B').upper()),
            schedules[0]  # fallback to the most recent schedule if no match
        )
        latest_schedule = current_schedule['schedule_code']
        schedule_year = current_schedule['effective_year']
        schedule_month = current_schedule['effective_month']

        print(f"Selected schedule: {latest_schedule} (Effective: {current_schedule['effective_date']})")

        print("Fetching items...")
        items = self.get_items(latest_schedule)
        time.sleep(5)

        print("Fetching indications...")
        indications = self.get_indications(latest_schedule)
        print(f"Number of indications fetched: {len(indications)}")
        print("Sample of raw indications data:")
        for indication in indications[:5]:
            print(indication)
        time.sleep(5)

        print("Fetching prescribing texts...")
        prescribing_texts = self.get_prescribing_texts(latest_schedule)
        time.sleep(5)

        print("Fetching item-prescribing-text relationships...")
        item_prescribing_text_relationships = self.get_item_prescribing_text_relationships(latest_schedule)
        time.sleep(5)

        print("Fetching restrictions...")
        restrictions = self.get_restrictions(latest_schedule)
        time.sleep(5)

        print("Fetching item-restriction relationships...")
        item_restriction_relationships = self.get_item_restriction_relationships(latest_schedule)

        print("Fetching restriction-prescribing-text relationships...")
        restriction_prescribing_text_relationships = self.get_restriction_prescribing_text_relationships(latest_schedule)
        print(f"Number of restriction-prescribing-text relationships fetched: {len(restriction_prescribing_text_relationships)}")
        time.sleep(5)

        # Create lookup dictionaries
        prescribing_text_lookup = {text['prescribing_txt_id']: text for text in prescribing_texts if 'prescribing_txt_id' in text}
        restriction_lookup = {res['res_code']: res for res in restrictions if 'res_code' in res}

        # Create indication lookup
        indication_lookup = {}
        for ind in indications:
            # Print all keys in the first indication to see available fields
            if not indication_lookup:
                print("Keys in indication data:", ind.keys())
            
            # Try different possible keys for the prescribing text ID
            prescribing_text_id = ind.get('prescribing_text_id') or ind.get('indication_prescribing_txt_id') or ind.get('prescribing_txt_id')
            if prescribing_text_id:
                indication_lookup[prescribing_text_id] = ind

        print(f"Number of items in indication_lookup: {len(indication_lookup)}")
        print("Sample of indication_lookup:")
        for key, value in list(indication_lookup.items())[:5]:
            print(f"  {key}: {value}")

        # Create a lookup for item-prescribing-text relationships
        item_prescribing_text_lookup = {}
        for relationship in item_prescribing_text_relationships:
            pbs_code = relationship.get('pbs_code')
            prescribing_txt_id = relationship.get('prescribing_txt_id')
            if pbs_code and prescribing_txt_id:
                if pbs_code not in item_prescribing_text_lookup:
                    item_prescribing_text_lookup[pbs_code] = []
                item_prescribing_text_lookup[pbs_code].append(prescribing_txt_id)

        # Create a lookup for restriction-prescribing-text relationships
        restriction_prescribing_text_lookup = {}
        print("\nDebugging restriction-prescribing-text relationships:")
        print("Full structure of first 5 relationships:")
        for relationship in restriction_prescribing_text_relationships[:5]:
            print(relationship)

        for relationship in restriction_prescribing_text_relationships:
            res_code = relationship.get('res_code')
            prescribing_text_id = relationship.get('prescribing_text_id')
            if res_code and prescribing_text_id:
                if res_code not in restriction_prescribing_text_lookup:
                    restriction_prescribing_text_lookup[res_code] = []
                restriction_prescribing_text_lookup[res_code].append(prescribing_text_id)

        print(f"Number of items in restriction_prescribing_text_lookup: {len(restriction_prescribing_text_lookup)}")
        print("Sample of restriction_prescribing_text_lookup:")
        for key, value in list(restriction_prescribing_text_lookup.items())[:5]:
            print(f"  {key}: {value}")

        print("Debugging: Inspecting lookups")
        print(f"Number of items in prescribing_text_lookup: {len(prescribing_text_lookup)}")
        print(f"Number of items in restriction_lookup: {len(restriction_lookup)}")
        print(f"Number of items in indication_lookup: {len(indication_lookup)}")
        print(f"Number of items in item_prescribing_text_lookup: {len(item_prescribing_text_lookup)}")
        print(f"Number of items in restriction_prescribing_text_lookup: {len(restriction_prescribing_text_lookup)}")

        def classify_formulation(description):
            # Define keywords for each formulation type
            tablet_keywords = ['Tablet']
            pen_keywords = ['pen', 'auto-injector', 'autoinjector']
            syringe_keywords = ['syringe']
            infusion_keywords = ['I.V. infusion', 'Concentrate for injection']

            # Normalize the description to lowercase for case-insensitive matching
            desc_lower = description.lower()

            # Check for keywords and return the corresponding formulation type
            if any(keyword.lower() in desc_lower for keyword in tablet_keywords):
                return 'tablet'
            elif any(keyword.lower() in desc_lower for keyword in pen_keywords):
                return 'subcut pen'
            elif any(keyword.lower() in desc_lower for keyword in syringe_keywords):
                return 'subcut syringe'
            elif any(keyword.lower() in desc_lower for keyword in infusion_keywords):
                return 'infusion'
            else:
                return 'unknown'  # For cases that don't match any category

        def classify_hospital_type(program_code):
            if program_code == 'HS':
                return 'Private'
            elif program_code == 'HB':
                return 'Public'
            else:
                return 'Any'

        for item in items:
            if any(biologic.lower() in item['drug_name'].lower() for biologic in biologics):
                pbs_code = item['pbs_code']
                if pbs_code not in data:
                    data[pbs_code] = {
                        "schedule_code": latest_schedule,
                        "schedule_year": schedule_year,
                        "schedule_month": schedule_month,
                        "name": item['drug_name'],
                        "brands": [],  # Change this to a list
                        "formulation": classify_formulation(item['li_form']),
                        "li_form": item['li_form'],
                        "schedule_form": item['schedule_form'],
                        "manner_of_administration": item['manner_of_administration'],
                        "maximum_quantity": item['maximum_quantity_units'],
                        "number_of_repeats": item['number_of_repeats'],
                        "hospital_type": classify_hospital_type(item['program_code']),
                        "restrictions": []
                    }
                # Append the brand name if it's not already in the list
                if item['brand_name'] not in data[pbs_code]['brands']:
                    data[pbs_code]['brands'].append(item['brand_name'])

        for pbs_code in list(data.keys()):
            for relationship in item_restriction_relationships:
                if relationship.get('pbs_code') == pbs_code:
                    res_code = relationship.get('res_code')
                    restriction = restriction_lookup.get(res_code)
                    if restriction:
                        prescribing_text_ids = restriction_prescribing_text_lookup.get(res_code, [])
                        for prescribing_text_id in prescribing_text_ids:
                            indication = indication_lookup.get(prescribing_text_id)
                            if indication:
                                condition = indication.get('condition', '').lower()
                                found_indication = next((disease for disease in rheumatic_diseases if disease.lower() in condition), None)
                                if found_indication:
                                    restriction_data = {
                                        'res_code': res_code,
                                        'indications': found_indication,
                                        'treatment_phase': restriction.get('treatment_phase', ''),
                                        'restriction_text': restriction.get('li_html_text', ''),
                                        'authority_method': restriction.get('authority_method', ''),
                                        'streamlined_code': restriction.get('treatment_of_code') if restriction.get('authority_method') == "STREAMLINED" else None,
                                        'online_application': "HOBART TAS 7001" not in restriction.get('schedule_html_text', '')
                                    }
                                    data[pbs_code]['restrictions'].append(restriction_data)
                                    break  # Stop after finding the first matching indication

        # Drop entries if restrictions are empty
        data = {k: v for k, v in data.items() if v['restrictions']}
        return data

    def preprocess_data(self, data):
        processed = {
            'combinations': []
        }
        
        for pbs_code, item in data.items():
            for restriction in item['restrictions']:
                for brand in item['brands']:
                    processed['combinations'].append({
                        'pbs_code': pbs_code,
                        'drug': item['name'],
                        'brand': brand,
                        'formulation': item['li_form'],
                        'indication': restriction['indications'],
                        'treatment_phase': restriction['treatment_phase'],
                        'streamlined_code': restriction['streamlined_code'],
                        'online_application': restriction['online_application'],
                        'authority_method': restriction['authority_method'],
                        'hospital_type': item['hospital_type'],
                        'schedule_code': item['schedule_code'],
                        'schedule_year': item['schedule_year'],
                        'schedule_month': item['schedule_month']
                    })
        
        return processed

    def save_data_to_hf(self, data, hf_token, dataset_name="cmcmaster/rheumatology-biologics-dataset"):
        processed_data = self.preprocess_data(data)
        
        # Create a Dataset from the combinations
        dataset = Dataset.from_list(processed_data['combinations'])
        
        # Push the dataset to the Hugging Face Hub
        dataset.push_to_hub(dataset_name, token=hf_token)
        
        print(f"Data saved to Hugging Face Hub: {dataset_name}")

def main():
    client = PBSPublicDataAPIClient("2384af7c667342ceb5a736fe29f1dc6b", rate_limit=0.2)

    try:
        print("Fetching data on biologics used for rheumatological diseases...")
        data = client.fetch_rheumatology_biologics_data()
        
        print(f"Data fetched for {len(data)} items.")
        
        client.save_data_to_hf(data)
        print("Data saved to Hugging Face Hub")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()