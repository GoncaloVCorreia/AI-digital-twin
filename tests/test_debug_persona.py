import pytest
from sqlalchemy import inspect

def test_debug_persona_table(db_session):
    """Debug: verifica a estrutura da tabela personas."""
    from app.models.persona_model import Persona
    from sqlalchemy import create_engine
    from tests.conftest import engine
    
    inspector = inspect(engine)
    
    # Lista todas as tabelas
    tables = inspector.get_table_names()
    print(f"\n📋 Tabelas disponíveis: {tables}")
    
    # Verifica constraints da tabela personas
    if "personas" in tables:
        columns = inspector.get_columns("personas")
        print(f"\n📊 Colunas da tabela 'personas':")
        for col in columns:
            print(f"  - {col['name']}: {col['type']} (nullable={col['nullable']})")
        
        # Verifica indexes e constraints
        indexes = inspector.get_indexes("personas")
        print(f"\n🔑 Indexes:")
        for idx in indexes:
            print(f"  - {idx}")
        
        pk = inspector.get_pk_constraint("personas")
        print(f"\n🔐 Primary Key: {pk}")
        
        unique_constraints = inspector.get_unique_constraints("personas")
        print(f"\n⚠️ UNIQUE Constraints: {unique_constraints}")
    
    # Tenta criar uma persona
    from tests.personas.factories import make_persona_create
    from app.services.persona_service import PersonaService
    
    payload = make_persona_create(name="Debug Test")
    print(f"\n🔍 Tentando criar persona com nome: {payload.name}")
    
    try:
        persona = PersonaService.create_persona(db_session, payload, creator_id=1)
        print(f"✅ Persona criada com sucesso! ID: {persona.id}")
        
        # Tenta criar outra com o mesmo nome
        payload2 = make_persona_create(name="Debug Test")
        persona2 = PersonaService.create_persona(db_session, payload2, creator_id=1)
        print(f"✅ Segunda persona criada! ID: {persona2.id}")
        print("⚠️ NÃO HÁ CONSTRAINT UNIQUE NO NOME!")
        
    except Exception as e:
        print(f"❌ Erro ao criar persona: {type(e).__name__}: {e}")
import pytest
from sqlalchemy import inspect

def test_debug_persona_table(db_session):
    """Debug: verifica a estrutura da tabela personas."""
    from app.models.persona_model import Persona
    from sqlalchemy import create_engine
    from tests.conftest import engine
    
    inspector = inspect(engine)
    
    # Lista todas as tabelas
    tables = inspector.get_table_names()
    print(f"\n📋 Tabelas disponíveis: {tables}")
    
    # Verifica constraints da tabela personas
    if "personas" in tables:
        columns = inspector.get_columns("personas")
        print(f"\n📊 Colunas da tabela 'personas':")
        for col in columns:
            print(f"  - {col['name']}: {col['type']} (nullable={col['nullable']})")
        
        # Verifica indexes e constraints
        indexes = inspector.get_indexes("personas")
        print(f"\n🔑 Indexes:")
        for idx in indexes:
            print(f"  - {idx}")
        
        pk = inspector.get_pk_constraint("personas")
        print(f"\n🔐 Primary Key: {pk}")
        
        unique_constraints = inspector.get_unique_constraints("personas")
        print(f"\n⚠️ UNIQUE Constraints: {unique_constraints}")
    
    # Tenta criar uma persona
    from tests.personas.factories import make_persona_create
    from app.services.persona_service import PersonaService
    
    payload = make_persona_create(name="Debug Test")
    print(f"\n🔍 Tentando criar persona com nome: {payload.name}")
    
    try:
        persona = PersonaService.create_persona(db_session, payload, creator_id=1)
        print(f"✅ Persona criada com sucesso! ID: {persona.id}")
        
        # Tenta criar outra com o mesmo nome
        payload2 = make_persona_create(name="Debug Test")  # mesmo nome!
        persona2 = PersonaService.create_persona(db_session, payload2, creator_id=1)
        print(f"✅ Segunda persona criada! ID: {persona2.id}")
        print("⚠️ NÃO HÁ CONSTRAINT UNIQUE NO NOME!")
        
    except Exception as e:
        print(f"❌ Erro ao criar persona: {type(e).__name__}: {e}")