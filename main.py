from fasthtml.common import *
from datasets import load_dataset
import datetime
from pbs_data import PBSPublicDataAPIClient
import os
from fasthtml_hf import setup_hf_backup
from fasthtml import FastHTML
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

HF_TOKEN = os.environ.get("HF_TOKEN")


custom_css = Style("""
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f0f0f0;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 30px;
    }
    form {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    label {
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
        color: #2c3e50;
    }
    select, button {
        width: 100%;
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: #fff;
        color: #333;
    }
    button {
        background-color: #3498db;
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    button:hover {
        background-color: #2980b9;
    }
    #results {
        margin-top: 30px;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    #results h2 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    #results p {
        margin-bottom: 10px;
        color: #333;
    }
    #results hr {
        border: none;
        border-top: 1px solid #eee;
        margin: 20px 0;
    }
    a {
        color: #3498db;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
""")

DATASET_NAME = "cmcmaster/rheumatology-biologics-dataset"

def load_data():
    try:
        dataset = load_dataset(DATASET_NAME, split="train")
        
        # Create sets for dropdown options
        drugs = set(dataset['drug'])
        brands = set(dataset['brand'])
        formulations = set(dataset['formulation'])
        indications = set(dataset['indication'])
        treatment_phases = set(dataset['treatment_phase'])
        hospital_types = set(dataset['hospital_type'])

        return {
            'combinations': dataset,
            'drugs': sorted(drugs),
            'brands': sorted(brands),
            'formulations': sorted(formulations),
            'indications': sorted(indications),
            'treatment_phases': sorted(treatment_phases),
            'hospital_types': sorted(hospital_types)
        }
    except Exception as e:
        print(f"An error occurred while loading data: {str(e)}")
        return {
            'combinations': [],
            'drugs': [],
            'brands': [],
            'formulations': [],
            'indications': [],
            'treatment_phases': [],
            'hospital_types': []
        }

biologics_data = load_data()

app, rt = fast_app()

def search_biologics(drug, brand, formulation, indication, treatment_phase, hospital_type):
    results = biologics_data['combinations'].filter(
        lambda x: (not drug or x['drug'] == drug) and
                  (not brand or x['brand'] == brand) and
                  (not formulation or x['formulation'] == formulation) and
                  (not indication or x['indication'] == indication) and
                  (not treatment_phase or x['treatment_phase'] == treatment_phase) and
                  (not hospital_type or x['hospital_type'] == hospital_type)
    )
    
    if len(results) == 0:
        return "No results found."
    
    output = ""
    for item in results:
        output += f"""
        <div class="result-item">
            <h2>{item['drug']} ({item['brand']})</h2>
            <p><strong>PBS Code:</strong> <a href="https://www.pbs.gov.au/medicine/item/{item['pbs_code']}" target="_blank">{item['pbs_code']}</a></p>
            <p><strong>Formulation:</strong> {item['formulation']}</p>
            <p><strong>Indication:</strong> {item['indication']}</p>
            <p><strong>Treatment Phase:</strong> {item['treatment_phase']}</p>
            <p><strong>Streamlined Code:</strong> {item['streamlined_code'] or 'N/A'}</p>
            <p><strong>Authority Method:</strong> {item['authority_method']}</p>
            <p><strong>Online Application:</strong> {'Yes' if item['online_application'] else 'No'}</p>
            <p><strong>Hospital Type:</strong> {item['hospital_type']}</p>
            <p><strong>Schedule Year:</strong> {item['schedule_year']}</p>
            <p><strong>Schedule Month:</strong> {item['schedule_month']}</p>
        </div>
        <hr>
        """
    
    return output

def update_options(drug, brand, formulation, indication, treatment_phase, hospital_type):
    filtered = biologics_data['combinations'].filter(
        lambda x: (not drug or x['drug'] == drug) and
                  (not brand or x['brand'] == brand) and
                  (not formulation or x['formulation'] == formulation) and
                  (not indication or x['indication'] == indication) and
                  (not treatment_phase or x['treatment_phase'] == treatment_phase) and
                  (not hospital_type or x['hospital_type'] == hospital_type)
    )
    
    options = {
        'drugs': sorted(set(filtered['drug'])),
        'brands': sorted(set(filtered['brand'])),
        'formulations': sorted(set(filtered['formulation'])),
        'indications': sorted(set(filtered['indication'])),
        'treatment_phases': sorted(set(filtered['treatment_phase'])),
        'hospital_types': sorted(set(filtered['hospital_type']))
    }
    
    return options

@rt('/')
def get():
    return Div(
        custom_css,
        H1("Biologics Prescriber Helper"),
        Form(
            Div(
                Label("Drug:"),
                Select(Option("All", value=""), *[Option(drug, value=drug) for drug in biologics_data['drugs']], name="drug", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Brand:"),
                Select(Option("All", value=""), *[Option(brand, value=brand) for brand in biologics_data['brands']], name="brand", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Formulation:"),
                Select(Option("All", value=""), *[Option(formulation, value=formulation) for formulation in biologics_data['formulations']], name="formulation", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Indication:"),
                Select(Option("All", value=""), *[Option(indication, value=indication) for indication in biologics_data['indications']], name="indication", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Treatment Phase:"),
                Select(Option("All", value=""), *[Option(phase, value=phase) for phase in biologics_data['treatment_phases']], name="treatment_phase", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Hospital Type:"),
                Select(Option("All", value=""), *[Option(ht, value=ht) for ht in biologics_data['hospital_types']], name="hospital_type", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Button("Search", type="submit"),
                Button("Reset", hx_get="/reset", hx_target="#options")
            ),
            hx_post="/search",
            hx_target="#results",
            id="options"
        ),
        Div(id="results")
    )

@rt('/reset')
def get():
    return Div(
        custom_css,
        Form(
            Div(
                Label("Drug:"),
                Select(Option("All", value=""), *[Option(drug, value=drug) for drug in biologics_data['drugs']], name="drug", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Brand:"),
                Select(Option("All", value=""), *[Option(brand, value=brand) for brand in biologics_data['brands']], name="brand", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Formulation:"),
                Select(Option("All", value=""), *[Option(formulation, value=formulation) for formulation in biologics_data['formulations']], name="formulation", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Indication:"),
                Select(Option("All", value=""), *[Option(indication, value=indication) for indication in biologics_data['indications']], name="indication", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Treatment Phase:"),
                Select(Option("All", value=""), *[Option(phase, value=phase) for phase in biologics_data['treatment_phases']], name="treatment_phase", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Hospital Type:"),
                Select(Option("All", value=""), *[Option(ht, value=ht) for ht in biologics_data['hospital_types']], name="hospital_type", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Button("Search", type="submit"),
                Button("Reset", hx_get="/reset", hx_target="#options")
            ),
            hx_post="/search",
            hx_target="#results",
            id="options"
        )
    )

@rt('/update_options')
def get(drug: str = '', brand: str = '', formulation: str = '', indication: str = '', treatment_phase: str = '', hospital_type: str = ''):
    options = update_options(drug, brand, formulation, indication, treatment_phase, hospital_type)
    return Div(
        custom_css,
        Form(
            Div(
                Label("Drug:"),
                Select(Option("All", value=""), *[Option(d, value=d, selected=(d == drug)) for d in options['drugs']], name="drug", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Brand:"),
                Select(Option("All", value=""), *[Option(b, value=b, selected=(b == brand)) for b in options['brands']], name="brand", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Formulation:"),
                Select(Option("All", value=""), *[Option(f, value=f, selected=(f == formulation)) for f in options['formulations']], name="formulation", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Indication:"),
                Select(Option("All", value=""), *[Option(i, value=i, selected=(i == indication)) for i in options['indications']], name="indication", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Treatment Phase:"),
                Select(Option("All", value=""), *[Option(p, value=p, selected=(p == treatment_phase)) for p in options['treatment_phases']], name="treatment_phase", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Label("Hospital Type:"),
                Select(Option("All", value=""), *[Option(ht, value=ht, selected=(ht == hospital_type)) for ht in options['hospital_types']], name="hospital_type", hx_get="/update_options", hx_target="#options", hx_trigger="change", hx_include="[name='drug'],[name='brand'],[name='formulation'],[name='indication'],[name='treatment_phase'],[name='hospital_type']")
            ),
            Div(
                Button("Search", type="submit"),
                Button("Reset", hx_get="/reset", hx_target="#options")
            ),
            hx_post="/search",
            hx_target="#results",
            id="options"
        )
    )

@rt('/search')
def post(drug: str = '', brand: str = '', formulation: str = '', indication: str = '', treatment_phase: str = '', hospital_type: str = ''):
    results = search_biologics(drug, brand, formulation, indication, treatment_phase, hospital_type)
    return results

def update_data():
    print(f"Updating data at {datetime.datetime.now()}")
    client = PBSPublicDataAPIClient("2384af7c667342ceb5a736fe29f1dc6b", rate_limit=0.2)
    try:
        data = client.fetch_rheumatology_biologics_data()
        client.save_data_to_hf(data, HF_TOKEN, DATASET_NAME)
        print("Data updated successfully")
        global biologics_data
        biologics_data = load_data()
    except Exception as e:
        print(f"An error occurred while updating data: {str(e)}")

# Set up the scheduler
update_data()
# Set up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=update_data,
    trigger=IntervalTrigger(hours=24),
    id='update_data',
    name='Update Data',
    replace_existing=True
)
scheduler.start()

# Make sure to shut down the scheduler when the app is terminated

atexit.register(lambda: scheduler.shutdown())

setup_hf_backup(app)
serve()