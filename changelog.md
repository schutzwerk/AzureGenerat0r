# Changelog
## [1.1] - 2021-08-05
- AzureGenerat0r used to deploy resources via Terraform modules. This approach required to code a Terraform module for each Azure resource. Changes have been made, so that AzureGenerat0r now can deploy [all AzureRM](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs) and [all AzureAD](https://registry.terraform.io/providers/hashicorp/azuread/latest/docs) resources. For example: To deploy a AzureRM resource like `azurerm_virtual_machine` use `virtual_machine`in your specification. To deploy a AzureAD resource like `azuread_service_principal` use `service_principal` in your specification.
- Every resource now has an internal id starting at zero
- You can connect resources as follows: CONNECT/\<id\>.\<attribute\>
- Plugins now can be used in a specification as follows: PLUGIN/\<pluginname\>
- Plugins are now hot loaded
- Default values for resources can be defined in the inner_mappings array in Controller.py
- Default connections to other resources can be defined in the outer_mappings array in Controller.py
- The examples in the specifications directory have been updated. You can find all details there.
