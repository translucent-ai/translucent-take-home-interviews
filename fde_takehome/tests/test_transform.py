from app.transform import transform_record
import json, pathlib

sample = json.loads((pathlib.Path(__file__).parent.parent / "data" / "sample_remittance.json").read_text())[0]

def test_transform_keys():
    out = transform_record(sample)
    assert set(out.keys()) == {"claim_id","amount","denial_reason","department","service_date"}
