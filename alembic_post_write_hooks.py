def validate_sql(filename, options):
    """Valida scripts SQL para ambientes de produção"""
    with open(filename) as f:
        content = f.read().lower()

        forbidden = ['drop schema', 'drop table', 'alter table']
        if any(cmd in content for cmd in forbidden):
            raise ValueError("Operação perigosa detectada no script de migration")
