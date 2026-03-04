import requests
import json
import os

def fetch_cif(pdb_id: str, cfg) -> str:
    dir_path = f"{cfg.data_dir}/{pdb_id}"
    file_path = f"{dir_path}/{pdb_id}.cif"

    if os.path.exists(file_path):
        return file_path

    os.makedirs(dir_path, exist_ok=True)

    url = f"https://files.rcsb.org/download/{pdb_id}.cif"
    try: 
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download {pdb_id}: {e}")

    with open(file_path, "wb") as f:
        f.write(resp.content)

    return file_path

def fetch_protein_json(pdb_id: str, cfg):
    dir_path = f"{cfg.data_dir}/{pdb_id}"
    file_path = f"{dir_path}/{pdb_id}.json"

    if os.path.exists(file_path):
        return file_path
    
    os.makedirs(dir_path, exist_ok=True)

    query = """
        {
          entry(entry_id: "%s") {
            struct {
              title
            }
            exptl {
              method
            }
            rcsb_entry_info {
              diffrn_resolution_high {
                value
              }
              deposited_polymer_monomer_count
              disulfide_bond_count
            }
            refine_hist {
              pdbx_number_atoms_protein
              pdbx_number_atoms_nucleic_acid
              pdbx_number_atoms_ligand
            }
            polymer_entities {
              rcsb_entity_source_organism {
                scientific_name
              }
              rcsb_polymer_entity_container_identifiers {
                uniprot_ids
              }
            }
          }
        }
        """ % pdb_id
    
    url = "https://data.rcsb.org/graphql"
    try: 
        resp = requests.post(url, json={"query": query}).json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch {pdb_id} metadata: {e}")

    with open(file_path, 'w') as f:
        json.dump(resp, f)

    return file_path



def fetch_ligand_json(pdb_id: str, cfg) -> str:
    dir_path = f"{cfg.data_dir}/{pdb_id}"
    file_path = f"{dir_path}/{pdb_id}_ligands.json"

    if os.path.exists(file_path):
        return file_path

    os.makedirs(dir_path, exist_ok=True)

    query = """
{
      entry(entry_id: "%s") {
        nonpolymer_entities {
          nonpolymer_entity_instances {
            rcsb_nonpolymer_entity_instance_container_identifiers {
              auth_seq_id
              comp_id
              auth_asym_id
            }
          }
          nonpolymer_comp {
            chem_comp {
              formula_weight
              name
              formula
            }
          }
        }
      }
    }
    """ % pdb_id
    url = "https://data.rcsb.org/graphql"
    try:
        resp = requests.post(url, json={"query": query}).json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch {pdb_id} ligand metadata: {e}")

    with open(file_path, 'w') as f:
        json.dump(resp, f)

    return file_path
        
