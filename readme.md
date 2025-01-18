# HASS & Proprietary CentralDvc integration
## To run HASS local dev environment
1. Follow: https://developers.home-assistant.io/docs/development_environment/
2. The dev container runs inside the WSL, therefore this repo should be also cloned inside the same WSL

## To properly develop and debug this repo inside HASS Dev Container, following steps are needed:

1. Modify **devcontainer.json** and add following while the source points to folder if this repository:
    ```json
    "mounts": [
    "source=/mnt/d/hass/hass-centraldvc_client,target=/workspaces/hass-core/config/custom_components_dev/centraldvc_client,type=bind,consistency=cached",
    "source=/mnt/d/hass/hass-centraldvc_client/custom_components/centraldvc_client,target=/workspaces/hass-core/config/custom_components/centraldvc_client,type=bind,consistency=cached",
    ]
