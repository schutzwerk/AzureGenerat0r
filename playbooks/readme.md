# How to develop playbooks for AzureGenerat0r? <br />
There are a few conventions for playbook development.
* Each playbook contains a `main.yml`, which is executed by AzureGenerat0r.
* For classification, place a playbook down the right path within the playbooks directory. `<OS>/<Type>/<Modulname>`
* Metadata related to a playbook is stored in a file called `metadata.yml`