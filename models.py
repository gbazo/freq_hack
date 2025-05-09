from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class Presenca(BaseModel):
    id_estudante: int
    nome_completo: str
    email: Optional[str] = None
    dia_07_05: int = 0  # 0: ausente, 1: presente, 2: data futura
    dia_08_05_19h: int = 0
    dia_08_05_20h: int = 0
    dia_09_05_19h: int = 0
    dia_09_05_20h: int = 0

class ResultadoPresenca(BaseModel):
    nome: str
    sobrenome: str
    presencas: Dict[str, str]
    
    class Config:
        schema_extra = {
            "example": {
                "nome": "João",
                "sobrenome": "Silva",
                "presencas": {
                    "07/05/2025": "Presente",
                    "08/05/2025 19:00": "Ausente",
                    "08/05/2025 20:00": "Ausente",
                    "09/05/2025 19:00": "Data Futura",
                    "09/05/2025 20:00": "Data Futura"
                }
            }
        }