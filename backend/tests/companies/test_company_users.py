import pytest
from app.models.empresa import Empresa
from app.models.usuarios_empresa import UsuarioEmpresa, RoleType, Permission
from app.core.security import get_password_hash

@pytest.fixture
def test_user_for_company(db_session):
    """Usuario de prueba con full_name"""
    from app.models.user import User
    user = User(
        username="company_user_test",
        email="companyuser@test.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Company Test User"  # OBLIGATORIO
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_create_company_user(db_session, test_company, test_user_for_company):
    """Test: Create company-user relationship"""
    company_user = UsuarioEmpresa(
        user_id=test_user_for_company.id,
        empresa_id=test_company.id,
        role=RoleType.ADMIN.value,
        permissions=[Permission.READ.value, Permission.WRITE.value]
    )
    db_session.add(company_user)
    db_session.commit()
    
    assert company_user.id is not None

def test_user_roles(db_session, test_company, test_user_for_company):
    """Test: Different user roles"""
    company_user = UsuarioEmpresa(
        user_id=test_user_for_company.id,
        empresa_id=test_company.id,
        role=RoleType.VIEWER.value,
        permissions=[Permission.READ.value]
    )
    db_session.add(company_user)
    db_session.commit()
    
    assert company_user.role == RoleType.VIEWER.value

def test_user_permissions(db_session, test_company, test_user_for_company):
    """Test: User permissions"""
    company_user = UsuarioEmpresa(
        user_id=test_user_for_company.id,
        empresa_id=test_company.id,
        role=RoleType.ADMIN.value,
        permissions=[Permission.READ.value, Permission.WRITE.value, Permission.DELETE.value]
    )
    db_session.add(company_user)
    db_session.commit()
    
    assert len(company_user.permissions) == 3

def test_owner_has_all_permissions(db_session, test_company, test_user_for_company):
    """Test: Owner has all permissions"""
    company_user = UsuarioEmpresa(
        user_id=test_user_for_company.id,
        empresa_id=test_company.id,
        role=RoleType.OWNER.value,
        permissions=[p.value for p in Permission]
    )
    db_session.add(company_user)
    db_session.commit()
    
    assert company_user.role == RoleType.OWNER.value

def test_multiple_users_same_company(db_session, test_company):
    """Test: Multiple users in same company"""
    from app.models.user import User
    
    # FULL_NAME ES OBLIGATORIO
    user1 = User(username="user1", email="u1@test.com", full_name="User One", hashed_password=get_password_hash("pass"))
    user2 = User(username="user2", email="u2@test.com", full_name="User Two", hashed_password=get_password_hash("pass"))
    db_session.add_all([user1, user2])
    db_session.commit()
    
    cu1 = UsuarioEmpresa(user_id=user1.id, empresa_id=test_company.id, role=RoleType.ADMIN.value)
    cu2 = UsuarioEmpresa(user_id=user2.id, empresa_id=test_company.id, role=RoleType.VIEWER.value)
    db_session.add_all([cu1, cu2])
    db_session.commit()
    
    company_users = db_session.query(UsuarioEmpresa).filter_by(empresa_id=test_company.id).all()
    assert len(company_users) == 2
