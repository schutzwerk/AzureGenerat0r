#source https://github.com/Azure/terraform-azurerm-vnet

resource "azurerm_virtual_network" "vnet" {
  name                = "${var.vnet_name}"
  location            = "${var.location}"
  address_space       = ["${var.address_space}"]
  resource_group_name = "${var.resource_group_name}"
  dns_servers         = "${var.dns_servers}"
}

resource "azurerm_subnet" "subnet" {
  name                      = "${var.subnet_names[count.index]}"
  virtual_network_name      = "${azurerm_virtual_network.vnet.name}"
  resource_group_name       = "${var.resource_group_name}"
  address_prefix            = "${var.subnet_prefixes[count.index]}"
  count                     = "${length(var.subnet_names)}"
  route_table_id            = "${var.route_table_ids[count.index]}"
  network_security_group_id = "${azurerm_network_security_group.nsgAzureGenerator.id}"
}

resource "azurerm_network_security_group" "nsgAzureGenerator" {
  location                        = "${var.location}"
  name                            = "nsgAzureGenerator"
  resource_group_name             = "${var.resource_group_name}"
}

resource "azurerm_network_security_rule" "defaultAzureGeneratorRule" {
  name                        = "defaultAzureGeneratorRule"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "${var.own_IP_Address}"
  destination_address_prefix  = "*"
  resource_group_name         = "${var.resource_group_name}"
  network_security_group_name = "${azurerm_network_security_group.nsgAzureGenerator.name}"
}
