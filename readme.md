# Ondrej's HASS Integrations
## To run HASS local dev environment
1. Follow: https://developers.home-assistant.io/docs/development_environment/
2. The dev container runs inside the WSL, therefore this repo should be also cloned inside the same WSL

## To properly develop and debug this repo inside HASS Dev Container, following steps are needed:

1. Modify **devcontainer.json** and add following while the source points to folder if this repository:
    ```json
    "mounts": [
    "source=/mnt/d/hass-integrations,target=/workspaces/hass-core/config/custom_components,type=bind,consistency=cached"
    ]

2. Modify **settings.json** in .vscode and add following to ensure this git repository is shown in git Source control pane:
    ```json
    "git.scanRepositories": [
        "config/custom_components"
    ],
    "git.ignoredRepositories": [
        "/workspaces/hass-core"
    ]