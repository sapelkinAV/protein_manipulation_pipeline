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


class IonType(Enum):
    KCl = "KCl"
    NaCl = "NaCl"
    CaCl2 = "CaCl2"
    MgCl2 = "MgCl2"


class IonConfiguration:
    def __init__(self, ion_concentration: float = 0.15, ion_type: IonType = IonType.KCl):
        self.ion_concentration = ion_concentration
        self.ion_type = ion_type

    @staticmethod
    def builder():
        return IonConfigurationBuilder()


class IonConfigurationBuilder:
    def __init__(self):
        self._ion_concentration = 0.15
        self._ion_type = IonType.KCl

    def ion_concentration(self, concentration: float):
        self._ion_concentration = concentration
        return self

    def ion_type(self, ion_type: IonType):
        self._ion_type = ion_type
        return self

    def build(self) -> IonConfiguration:
        return IonConfiguration(
            ion_concentration=self._ion_concentration,
            ion_type=self._ion_type
        )


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

    @staticmethod
    def builder():
        return MembraneConfigBuilder()


class PdbFileOptionRequest:
    def __init__(self,
                 pdb_id: str,
                 file_input_mode: ProteinStructure,
                 file_path: Path = None,
                 email: str = None,
                 membrane_config: MembraneConfig = None,
                 input_protein_size_plus: int = 20,
                 water_thickness_z: float = 22.5,
                 ion_configuration: IonConfiguration = None,
                 temperature: float = 303.15,
                 perform_charmm_minimization: bool = True,
                 ):
        self.pdb_id = pdb_id
        self.file_input_mode = file_input_mode
        self.file_path = file_path
        self.output_dir = Path(f"/Users/sapelkinav/code/python/oprlm/data/pdb/step1_output/{pdb_id}")
        self.email = email
        self.membrane_config = membrane_config or MembraneConfig()
        self.input_protein_size_plus = input_protein_size_plus
        self.water_thickness_z = water_thickness_z
        self.ion_configuration = ion_configuration or IonConfiguration()
        self.temperature = temperature
        self.perform_charmm_minimization = perform_charmm_minimization

    @staticmethod
    def builder():
        return PdbFileOptionRequestBuilder()


class MembraneConfigBuilder:
    def __init__(self):
        self._membrane_type = MembraneType.CUSTOM
        self._popc = True
        self._dopc = False
        self._dspc = False
        self._dmpc = False
        self._dppc = False
        self._chol_value = 20.0
        self._protein_topology = ProteinTopologyMembrane.IN

    def membrane_type(self, membrane_type: MembraneType):
        self._membrane_type = membrane_type
        return self

    def popc(self, value: bool):
        self._popc = value
        return self

    def dopc(self, value: bool):
        self._dopc = value
        return self

    def dspc(self, value: bool):
        self._dspc = value
        return self

    def dmpc(self, value: bool):
        self._dmpc = value
        return self

    def dppc(self, value: bool):
        self._dppc = value
        return self

    def chol_value(self, value: float):
        self._chol_value = value
        return self

    def protein_topology(self, topology: ProteinTopologyMembrane):
        self._protein_topology = topology
        return self

    def build(self) -> MembraneConfig:
        return MembraneConfig(
            membrane_type=self._membrane_type,
            popc=self._popc,
            dopc=self._dopc,
            dspc=self._dspc,
            dmpc=self._dmpc,
            dppc=self._dppc,
            chol_value=self._chol_value,
            protein_topology=self._protein_topology
        )


class PdbFileOptionRequestBuilder:
    def __init__(self):
        self._pdb_id = None
        self._file_input_mode = None
        self._file_path = None
        self._email = None
        self._membrane_config = None
        self._input_protein_size_plus = 20
        self._water_thickness_z = 22.5
        self._ion_configuration = None
        self._temperature = 303.15

    def pdb_id(self, pdb_id: str):
        self._pdb_id = pdb_id
        return self

    def file_input_mode(self, mode: ProteinStructure):
        self._file_input_mode = mode
        return self

    def file_path(self, path: Path):
        self._file_path = path
        return self

    def email(self, email: str):
        self._email = email
        return self

    def membrane_config(self, config: MembraneConfig):
        self._membrane_config = config
        return self

    def input_protein_size_plus(self, input_protein_size_plus: int):
        self._input_protein_size_plus = input_protein_size_plus
        return self

    def water_thickness_z(self, water_thickness_z: float):
        self._water_thickness_z = water_thickness_z
        return self

    def ion_configuration(self, ion_configuration: IonConfiguration):
        self._ion_configuration = ion_configuration
        return self

    def temperature(self, temperature: float):
        self._temperature = temperature
        return self

    def perform_charmm_minimization(self, perform_minimization: bool):
        self._perform_charmm_minimization = perform_minimization
        return self

    def build(self) -> PdbFileOptionRequest:
        if self._pdb_id is None:
            raise ValueError("pdb_id is required")
        if self._file_input_mode is None:
            raise ValueError("file_input_mode is required")
        return PdbFileOptionRequest(
            pdb_id=self._pdb_id,
            file_input_mode=self._file_input_mode,
            file_path=self._file_path,
            email=self._email,
            membrane_config=self._membrane_config,
            input_protein_size_plus=self._input_protein_size_plus,
            water_thickness_z=self._water_thickness_z,
            ion_configuration=self._ion_configuration,
            temperature=self._temperature,
            perform_charmm_minimization=self._perform_charmm_minimization
        )