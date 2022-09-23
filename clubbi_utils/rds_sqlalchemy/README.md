# RDS SQLAlchemy

As long as we use AWS RDS and sqlalchemy together this package 

### Alembic

Usually when using alembic we need an env.py file

Here we provided an alembic_env_factory module that reduce copy-and-paste and make it use to run againts RDS instances.

 
```py
from clubbi_utils.rds_sqlalchemy.alembic_env_factory import run_alembic_env

from myproject import my_metadata

run_alembic_env(my_metadata)
```

To configure RDS you'll need change alembic.ini and set ALEMBIC_RDS_ENVIRONMENT variable.

This is useful for running migrations agains `staging` and `production`

```ini
[rds.production]
instance_id = rds_instance_id
database_name = database_name
user_name = user_name
password_secret_id = password_secrets_manager_id

[rds.staging]
instance_id = stg_rds_instance_id
database_name = stg_database_name
user_name = stg_user_name
password_secret_id = stg_password_secrets_manager_id
```

*Note: A common mistake is quote values inside init files.* 