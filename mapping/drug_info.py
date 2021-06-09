from dataclasses import dataclass


@dataclass
class DrugInfo:
    # first 3 fields are keys to link back to original database
    primaryid: int
    caseid: int
    drug_seq: int
    ###

    drug_name: str
    active_ingredient: str
    nda_number: int
    mapping: int = None  # rxcui

    # TODO: find a way to do this automatically instead of hardcoding the fields in str repr
    def __str__(self):
        return f'{self.primaryid},{self.caseid},{self.drug_seq},' \
               f'{self.drug_name},{self.active_ingredient},{self.nda_number},' \
               f'{self.mapping}'
