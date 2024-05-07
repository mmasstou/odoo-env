import os
import yaml
from dotenv import load_dotenv

# Get the present working directory

load_dotenv()

current_dir = os.getcwd()

print(f"+> : {current_dir}")
kzm_enterprise = "enterprise"
kzm_odoo_path = f"{current_dir}/odoo"
kzm_odoo_path = f"{current_dir}/enterprise"


repos = ["odoo", "enterprise", "extra-addons"]


def create_folder(_path):
    os.makedirs(_path)


for rep in repos:
    create_folder(f"{current_dir}/" + str(rep))

# Define the dictionary representing the docker-compose.yml content
compose_data = {
    "version": "3.8",
    "name": "kzm-odoo",
    "services": {
        "odoo": {
            "image": "registry.gitlab.com/odoo-kzm/gitlab_ci/odoo_images:odoo17_base",
            "container_name": "odoo",
            "env_file": [".env"],
            "volumes": [
                f"{current_dir}/configs/odoo.conf:/etc/odoo/odoo.conf:rw",
                "./mnt/extra-addons/custom:/mnt/extra-addons/custom:rw",
                "kzm_odoo:/usr/lib/python3/dist-packages/odoo:ro",
                "kzm_enterprise:/mnt/extra-addons/enterprise:ro",
            ],
            "ports": ["8019:8069"],
            "depends_on": ["db"],
            "networks": ["kzm_env_network"],
        },
        "database": {
            "image": "postgres:16",
            "container_name": "database",
            "env_file": [".env"],
            # 'volumes': ['- postgres-data:/var/lib/postgresql/data'],
            "networks": ["kzm_env_network"],
        },
        "portainer": {
            "build": {"context": "./services/portainer", "dockerfile": "Dockerfile"},
            "container_name": "portainer",
            "ports": ["4242:9443"],
            "volumes": [
                "/var/run/docker.sock:/var/run/docker.sock:ro",
                "kzm_portainer:/data",
            ],
            "networks": ["kzm_env_network"],
            "restart": "always",
        },
        "adminer": {
            "image": "dockette/adminer:latest",
            "restart": "always",
            "ports": ["8080:80"],
            "environment": {
                "ADMINER_DEFAULT_SERVER": "db",
                "ADMINER_ROOT_PASSWORD": "odoo",
            },
            "networks": ["kzm_env_network"],
        },
    },
    "volumes": {
        "kzm_portainer": None,
        "kzm_odoo": {
            "driver_opts": {
                "type": "volume",
                "o": "bind",
                "device": f"{current_dir}/odoo",
            }
        },
        "kzm_enterprise": {
            "driver_opts": {
                "type": "volume",
                "o": "bind",
                "device": f"{current_dir}/enterprise",
            }
        },
    },
    "networks": {"kzm_env_network": {"name": "kzm_env_network"}},
}

# Convert the dictionary to YAML format
yaml_content = yaml.dump(compose_data)

# Write the YAML content to a file
with open(f"{current_dir}/docker-compose.yml", "w") as file:
    file.write(yaml_content)
