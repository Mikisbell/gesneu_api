"""
Metadata registry centralizado para evitar conflictos SQLAlchemy.
"""
from sqlalchemy import MetaData

# Registry único para toda la aplicación
app_metadata = MetaData()
