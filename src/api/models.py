from enum import Enum
from pathlib import Path


class ProteinStructure(Enum):
    RCSB = "searchPDB"  # RCSB
    OPRLM = "searchOPM"  # OPRLM
    CUSTOM = "upload"  # CUSTOM


class MembraneType(Enum):
    CUSTOM = "custom"  # Simple model membrane
    PM_MAMMALIAN = "PMm"  # Plasma membrane (mammalian)
    PM_PLANTS = "PMp"  # Plasma membrane (plants)
    PM_FUNGI = "PMf"  # Plasma membrane (Fungi)
    ER_FUNGI = "ERf"  # ER (fungi)
    ER_MAMMALIAN = "ERm"  # ER (mammalian)
    GOLGI_MAMMALIAN = "GOLm"  # Golgi membrane (mammalian)
    GOLGI_FUNGI = "GOLf"  # Golgi membrane (fungi)
    ENDOSOME_MAMMALIAN = "ENDm"  # Endosome membrane (mammalian)
    LYSOSOME_MAMMALIAN = "LYSm"  # Lysosome membrane (mammalian)
    OUTER_MITOCHONDRIAL = "MOM"  # Outer mitochondrial membrane
    INNER_MITOCHONDRIAL = "MIM"  # Inner mitochondrial membrane
    VACUOLE = "VACp"  # Vacuole membrane (plants)
    THYLAKOID_PLANTS = "THYp"  # Thylakoid membrane (plants)
    THYLAKOID_CYANOBACTERIA = "THYc"  # Thylakoid membrane (cyanobacteria)
    BACT_OUTER = "BOUT"  # Outer membrane (Gram-negative bacteria)
    BACT_INNER = "BIN"  # Inner membrane (Gram-negative bacteria)
    BACT_POSITIVE = "BPM"  # Plasma membrane (Gram-positive bacteria)
    ARCHAEA = "APM"  # Archaeal plasma membrane
    GRAM_NEGATIVE_BACTERIA_OUTER_MEMBRANE = "G-OM"  # Gram-negative bacteria outer membrane
    GRAM_NEGATIVE_BACTERIA_INNER_MEMBRANE = "G-IM"  # Gram-negative bacteria inner membrane
    GRAM_POSITIVE_BACTERIA_MEMBRANE = "G-IM"  # Gram-positive bacteria membrane


class ProteinTopologyMembrane(Enum):
    IN = "in"
    OUT = "out"


class MembraneConfig:
    def __init__(self,
                 membrane_type: MembraneType = MembraneType.CUSTOM,
                 # OPRLM FOR SIMPLE MEMBRANE
                 popc: bool = True,
                 dopc: bool = False,
                 dspc: bool = False,
                 dmpc: bool = False,
                 dppc: bool = False,
                 chol_value: float = 20.0,
                 # RCSB AND UPLOAD
                 protein_topology: ProteinTopologyMembrane = ProteinTopologyMembrane.IN
                 ):
        self.membrane_type = membrane_type
        self.popc = popc
        self.dopc = dopc
        self.dspc = dspc
        self.dmpc = dmpc
        self.dppc = dppc
        self.chol_value = chol_value
        self.protein_topology = protein_topology


class PdbFileOptionRequest:
    def __init__(self,
                 pdb_id: str,
                 file_input_mode: ProteinStructure,
                 file_path: Path = None,
                 email: str = None,
                 membrane_config: MembraneConfig = None,
                 ):
        self.pdb_id = pdb_id
        self.file_input_mode = file_input_mode
        self.file_path = file_path
        self.output_dir = Path(f"/Users/sapelkinav/code/python/oprlm/data/pdb/step1_output/{pdb_id}")
        self.email = email
        self.membrane_config = membrane_config or MembraneConfig()