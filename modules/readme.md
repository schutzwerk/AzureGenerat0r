# How to develop modules? <br />
There are a few conventions for module development.
* A module contains a playbook named `main.yml`. It is called by AzureGenerat0r.
* For classification, place a module down the right path within the modules directory. `<OS>/<Type>/<Modulname>`
* Metadata related to a module is stored in a file called `metadata.yml`